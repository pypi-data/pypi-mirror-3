#include <Python.h>
#include "structmember.h"

#include "pam.h"
#include <pthread.h>

typedef enum {
    ctxflag_open_session = 0x01,
    ctxflag_elevated = 0x02
} handle_flag;

typedef struct {
    PyObject_HEAD
    pam_handle_t *handle;
    handle_flag flags;
    int rc;
    pthread_mutex_t lock;
    PyObject *environment;
} handle;

typedef struct {
    PyObject_HEAD
    handle *parent;
} environment;

typedef struct {
    PyObject_HEAD
    char **envlist;
    char **envp;
} environment_iter;

typedef struct {
    PyObject *conv;
#if HAS_PAM_FAIL_DELAY
    PyObject *delay;
#endif
    PyObject *data;
} opaque_data;

static PyObject *_pam_module;
static PyObject *PamError;
static PyObject *_gp_module;
static PyObject *_gp_fn;

#pragma region Defines

static PyObject *pam_rc_abort;
static PyObject *pam_rc_acct_exp;
static PyObject *pam_rc_authinfo_unavail;
static PyObject *pam_rc_authtok_disage;
static PyObject *pam_rc_authtok_err;
static PyObject *pam_rc_authtok_exp;
static PyObject *pam_rc_authtok_busy;
static PyObject *pam_rc_authtok_recerr;
static PyObject *pam_rc_auth_err;
static PyObject *pam_rc_buf_err;
static PyObject *pam_rc_conv_err;
static PyObject *pam_rc_cred_err;
static PyObject *pam_rc_cred_exp;
static PyObject *pam_rc_cred_insuff;
static PyObject *pam_rc_cred_unavail;
#if !IMPL_LINUX_PAM
static PyObject *pam_rc_domain_unk;
#endif
static PyObject *pam_rc_ignore;
static PyObject *pam_rc_maxtries;
static PyObject *pam_rc_module_unk;
static PyObject *pam_rc_new_authtok_req;
static PyObject *pam_rc_no_module_data;
static PyObject *pam_rc_open_err;
static PyObject *pam_rc_perm_denied;
static PyObject *pam_rc_service_err;
static PyObject *pam_rc_session_err;
static PyObject *pam_rc_success;
static PyObject *pam_rc_symbol_err;
static PyObject *pam_rc_system_err;
static PyObject *pam_rc_try_again;
static PyObject *pam_rc_user_unk;

static PyObject *pam_style_prompt_echo_off;
static PyObject *pam_style_prompt_echo_on;
static PyObject *pam_style_error_msg;
static PyObject *pam_style_text_info;

#define PAM_DEFINE(var, flag) do {                      \
    var = Py_BuildValue("I", flag);                     \
    Py_INCREF(var);                                     \
    PyModule_AddObject(_pam_module, #flag, var);        \
} while (0)

static inline void _populate_styles(void)
{
    PAM_DEFINE(pam_style_prompt_echo_off, PAM_PROMPT_ECHO_OFF);
    PAM_DEFINE(pam_style_prompt_echo_on, PAM_PROMPT_ECHO_ON);
    PAM_DEFINE(pam_style_error_msg, PAM_ERROR_MSG);
    PAM_DEFINE(pam_style_text_info, PAM_TEXT_INFO);
}

#pragma endregion -

#pragma region environment_iter implementation

static void environment_iter_dealloc(environment_iter *self)
{
    /* no guarantee iterator has been exhausted; ensure items are freed */
    if (*(self->envp) != NULL)
    {
        char **envp;
        for (envp=self->envp; *envp!=NULL; ++envp)
        {
            free(*envp);
        }
    }
    self->envp = NULL;
    free(self->envlist);
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject *environment_iter_iter(environment_iter *self)
{
    return (PyObject *)self;
}

static PyObject *environment_iter_next(environment_iter *self)
{
    if (*(self->envp) == NULL)
    {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }
    char *key, *val;
    val = *(self->envp);
    key = strsep(&val, "=");
    PyObject *r = Py_BuildValue("s", key);
    free(*(self->envp));
    ++(self->envp);
    return r;
}

static PyTypeObject environment_iterType = {
    PyObject_HEAD_INIT(NULL)
    /* ob_size */           0,
    /* tp_name */           "environment_iter",
    /* tp_basicsize */      sizeof(environment_iter),
    /* tp_itemsize */       0,
    /* tp_dealloc */        (destructor)environment_iter_dealloc,
    /* tp_print */          0,
    /* tp_getattr */        0,
    /* tp_setattr */        0,
    /* tp_compare */        0,
    /* tp_repr */           0,
    /* tp_as_number */      0,
    /* tp_as_sequence */    0,
    /* tp_as_mapping */     0,
    /* tp_hash */           0,
    /* tp_call */           0,
    /* tp_str */            0,
    /* tp_getattro */       0,
    /* tp_setattro */       0,
    /* tp_as_buffer */      0,
    /* tp_flags */          Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    /* tp_doc */            "environment_iter objects",
    /* tp_traverse */       0,
    /* tp_clear */          0,
    /* tp_richcompare */    0,
    /* tp_weaklistoffset */ 0,
    /* tp_iter */           (getiterfunc)environment_iter_iter,
    /* tp_iternext */       (iternextfunc)environment_iter_next,
    /* tp_methods */        0,
    /* tp_members */        0,
    /* tp_getset */         0,
    /* tp_base */           0,
    /* tp_dict */           0,
    /* tp_descr_get */      0,
    /* tp_descr_set */      0,
    /* tp_dictoffset */     0,
    /* tp_init */           0,
    /* tp_alloc */          PyType_GenericAlloc,
    /* tp_new */            PyType_GenericNew,
    /* tp_free */           0,
    /* tp_is_gc */          0,
    /* tp_bases */          0,
    /* tp_mro */            0,
    /* tp_cache */          0,
    /* tp_subclasses */     0,
    /* tp_weaklist */       0,
    /* tp_del */            0,
    /* tp_version_tag */    0,
};

#pragma endregion -

#pragma region environment implementation

static void environment_dealloc(environment *self)
{
    /* will be called during destructor for self->parent */
    self->parent = NULL;
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject *environment_subscr(environment *self, PyObject *key)
{
    const char *kstr = PyString_AsString(key);
    if (kstr == NULL) { return NULL; }
    const char *val = pam_getenv(self->parent->handle, kstr);
    if (val == NULL)
    {
        PyErr_Format(PyExc_KeyError, "%s", kstr);
        return NULL;
    }
    return Py_BuildValue("s", val);
}

static int environment_subscr_set(environment *self, PyObject *key, PyObject *val)
{
    const char *kstr = PyString_AsString(key);
    if (kstr == NULL) { return -1; }
    PyObject *vobj = PyObject_Str(val);
    if (vobj == NULL) { return -1; }
    const char *vstr = PyString_AsString(vobj);
    Py_DECREF(vobj);
    if (vstr == NULL) { return -1; }
    if (!strcmp(vstr, "<NULL>")) /* check for deletion */
    {
#if HAS_PAM_UNSETENV
        int rc = pam_unsetenv(self->parent->handle, kstr);
        self->parent->rc = rc;
        if (rc == PAM_SUCCESS) { return 0; }
        else {
            const char *errstr = pam_strerror(self->parent->handle, rc);
            PyErr_SetObject(PamError, Py_BuildValue("(is)", rc, errstr));
            return -1;
        }
#else
        PyErr_Format(PyExc_TypeError, "can't delete key '%s'", kstr);
        return -1;
#endif
    }
    
    char *kv = calloc(strlen(kstr) + strlen(vstr) + 1, sizeof(char));
    if (kv == NULL)
    {
        return -1;
    }
    sprintf(kv, "%s=%s", kstr, vstr);
    
    int rc = pam_putenv(self->parent->handle, (const char *)kv);
    self->parent->rc = rc;
    free(kv);
    if (rc != PAM_SUCCESS)
    {    
        const char *errstr = pam_strerror(self->parent->handle, rc);
        PyErr_SetObject(PamError, Py_BuildValue("(is)", rc, errstr));
        return -1;
    }
    
    return 0;
}

static Py_ssize_t environment_length(environment *self)
{
    char **envlist, **env;
    envlist = pam_getenvlist(self->parent->handle);
    if (envlist == NULL)
    {
        int rc = PAM_SYSTEM_ERR;
        const char *errstr = pam_strerror(self->parent->handle, rc);
        PyErr_SetObject(PamError, Py_BuildValue("(is)", rc, errstr));
        return -1;
    }
    Py_ssize_t s = 0;
    for (env=envlist; *env!=NULL; ++env)
    {
        ++s;
        free(*env);
    }
    free(envlist);
    return s;
}

static PyObject *environment_getiter(environment *self)
{
    char **envp = pam_getenvlist(self->parent->handle);
    if (envp == NULL)
    {
        int rc = PAM_SYSTEM_ERR;
        const char *errstr = pam_strerror(self->parent->handle, rc);
        PyErr_SetObject(PamError, Py_BuildValue("(is)", rc, errstr));
        return NULL;
    }
    PyObject *i = PyType_GenericNew((PyTypeObject *)&environment_iterType, NULL, NULL);
    if (i == NULL) { return NULL; }
    ((environment_iter *)i)->envlist = envp;
    ((environment_iter *)i)->envp = envp;
    return i;
}

#if !ENVIRON_REPR_OPAQUE
static PyObject *environment_repr(environment *self)
{
    char **envlist;
    char **env;
    envlist = pam_getenvlist(self->parent->handle);
    if (envlist == NULL)
    {
        return Py_BuildValue("s", "{}");
    }
    PyObject *rdict = PyDict_New();
    if (rdict == NULL)
    {
        return NULL;
    }
    char *key;
    char *val;
    PyObject *value;
    for (env=envlist; *env!=NULL; ++env)
    {
        val = *env;
        key = strsep(&val, "=");
        value = Py_BuildValue("s", val);
        PyDict_SetItemString(rdict, key, value);
        free(*env);
        Py_XDECREF(value);
    }
    PyObject *repr = PyObject_Repr(rdict);
    Py_XDECREF(rdict);
    return repr;
}
#endif

static PyMappingMethods environment_map_methods = {
    (lenfunc)environment_length,
    (binaryfunc)environment_subscr,
    (objobjargproc)environment_subscr_set
};

static PyTypeObject environmentType = {
    PyObject_HEAD_INIT(NULL)
    /* ob_size */           0,
    /* tp_name */           "environment",
    /* tp_basicsize */      sizeof(environment),
    /* tp_itemsize */       0,
    /* tp_dealloc */        (destructor)environment_dealloc,
    /* tp_print */          0,
    /* tp_getattr */        0,
    /* tp_setattr */        0,
    /* tp_compare */        0,
#if !ENVIRON_REPR_OPAQUE
    /* tp_repr */           (reprfunc)environment_repr,
#else
    /* tp_repr */           0,
#endif
    /* tp_as_number */      0,
    /* tp_as_sequence */    0,
    /* tp_as_mapping */     &environment_map_methods,
    /* tp_hash */           0,
    /* tp_call */           0,
    /* tp_str */            0,
    /* tp_getattro */       0,
    /* tp_setattro */       0,
    /* tp_as_buffer */      0,
    /* tp_flags */          Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    /* tp_doc */            "environment objects",
    /* tp_traverse */       0,
    /* tp_clear */          0,
    /* tp_richcompare */    0,
    /* tp_weaklistoffset */ 0,
    /* tp_iter */           (getiterfunc)environment_getiter,
    /* tp_iternext */       0,
    /* tp_methods */        0,
    /* tp_members */        0,
    /* tp_getset */         0,
    /* tp_base */           0,
    /* tp_dict */           0,
    /* tp_descr_get */      0,
    /* tp_descr_set */      0,
    /* tp_dictoffset */     0,
    /* tp_init */           0,
    /* tp_alloc */          PyType_GenericAlloc,
    /* tp_new */            PyType_GenericNew,
    /* tp_free */           0,
    /* tp_is_gc */          0,
    /* tp_bases */          0,
    /* tp_mro */            0,
    /* tp_cache */          0,
    /* tp_subclasses */     0,
    /* tp_weaklist */       0,
    /* tp_del */            0,
    /* tp_version_tag */    0,
};

#pragma endregion -

#pragma region handle implementation

#define PAM_API(fn, ...) do { self->rc = fn(__VA_ARGS__); } while (0)

static int _pam_conversation(int num_msg, const struct pam_message **msg,
                             struct pam_response **resp, void *appdata_ptr)
{
    int i;
    const struct pam_message *current;
    PyObject *callback = ((opaque_data *)appdata_ptr)->conv;
    PyObject *data = ((opaque_data *)appdata_ptr)->data;
    PyObject *retval;
    for (i=0; i<num_msg; ++i)
    {
        current = msg[i];
        retval = PyObject_CallFunction(callback, "IsO",
                                       current->msg_style,
                                       current->msg,
                                       data);
        if (retval != NULL)
        {
            *resp = malloc(sizeof(struct pam_response));
            if (current->msg_style == PAM_PROMPT_ECHO_OFF
             || current->msg_style == PAM_PROMPT_ECHO_ON)
            {
                if (retval == Py_None)
                {
                    (*resp)->resp = NULL;
                } else {
                    // handle user response
                    char *temp = PyString_AsString(retval);
                    if (temp == NULL)
                    {
                        PyErr_Clear();
                        return PAM_CONV_ERR;
                    }
                    size_t len = strlen(temp);
                    (*resp)->resp = calloc(len+1, sizeof(char));
                    strncpy((*resp)->resp, temp, len);
                }
            } else {
                (*resp)->resp = NULL;
            }
            (*resp)->resp_retcode = 0;
        } else {
            PyErr_Clear();
            return PAM_CONV_ERR;
        }
    }
    PyErr_Clear();
    return PAM_SUCCESS;
}

static PyObject *_conv_callback(PyObject *self, PyObject *args)
{
    int msg_style;
    char *msg;
    PyObject *data;

    if (!PyArg_ParseTuple(args, "IsO", &msg_style, &msg, &data))
    {
        return NULL;
    }
    PyObject *result;
    char *line;
    size_t linecap;
    ssize_t linelen;

    switch (msg_style)
    {
        case PAM_PROMPT_ECHO_OFF:
        result = PyObject_CallFunction(_gp_fn, "s", msg);
        return result;
        break;

        case PAM_PROMPT_ECHO_ON:
        line = NULL;
        linecap = 0;
        linelen = getline(&line, &linecap, stdin);
        result = Py_BuildValue("s", line);
        return result;
        break;

        case PAM_ERROR_MSG:
        fprintf(stderr, "%s\n", msg);
        Py_RETURN_NONE;
        break;

        case PAM_TEXT_INFO:
        fprintf(stdout, "%s\n", msg);
        Py_RETURN_NONE;
        break;
    }

    Py_RETURN_NONE;
}

static void handle_dealloc(handle *self)
{
    if (self->flags & ctxflag_open_session)
    {
        PAM_API(pam_close_session, self->handle, PAM_SILENT);
        self->flags ^= ctxflag_open_session;
    }
    PAM_API(pam_end, self->handle, self->rc);
    PyObject *e = self->environment;
    self->environment = NULL;
    Py_XDECREF(e);
    self->handle = NULL;
    pthread_mutex_destroy(&(self->lock));
    self->ob_type->tp_free((PyObject *)self);
}

static int
handle_init(handle *self, PyObject *args, PyObject *kws)
{
    const char *service = DEFAULT_SERVICE;      // defined by setup.py
    const char *user = NULL;
    PyObject *conv_cb = NULL;
    PyObject *data = NULL;
#if !HAS_PAM_FAIL_DELAY
    static char *kwlist[] = {"service", "user", "conv", "data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kws, "|ssOO", kwlist,
                                     &service, &user, &conv_cb, &data))
#else
    PyObject *delay_cb = NULL;
    static char *kwlist[] = {"service", "user",
                             "conv", "delay", "data", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kws, "|ssOOO", kwlist,
                                     &service, &user, &conv_cb, &delay_cb, &data))
#endif
    {
        return -1;
    }
    
    int mutex_rc = pthread_mutex_init(&(self->lock), NULL);
    if (mutex_rc != 0)
    {
        PyErr_SetFromErrno(PyExc_EnvironmentError);
        return -1;
    }
    
    if (user == NULL)
    {
        struct passwd pwdbuf;
        char buf[1024];
        struct passwd *pwd;
        int errnum = getpwuid_r(getuid(), &pwdbuf, buf, 1024, &pwd);
        if (errnum != 0 || pwd == NULL)
        {
            PyErr_SetString(PyExc_EnvironmentError,
                            "unable to determine current user");
            return -1;
        }
        user = (const char *)(pwd->pw_name);
    }
    
    if (conv_cb == NULL)
    {
        conv_cb = PyObject_GetAttrString(_pam_module, "_conv_callback");
        if (conv_cb == NULL) { return -1; }
    }
#if HAS_PAM_FAIL_DELAY
    if (delay_cb == NULL)
    {
        delay_cb = PyObject_GetAttrString(_pam_module, "_delay_callback");
        if (delay_cb == NULL) { return -1; }
    }
#endif
    if (data == NULL)
    {
        data = Py_None;
        Py_INCREF(Py_None);
    }
    
    PyObject *e = PyType_GenericNew((PyTypeObject *)&environmentType, NULL, NULL);
    if (e == NULL) { return -1; }
    Py_INCREF(e);
    ((environment *)e)->parent = self;
    self->environment = e;
    
    self->flags = 0;
    
    opaque_data *opq = malloc(sizeof(opaque_data));
    if (opq == NULL)
    {
        Py_DECREF(e);
        return -1;
    }
    Py_INCREF(conv_cb);
    opq->conv = conv_cb;
    opq->data = data;
#if HAS_PAM_FAIL_DELAY
    Py_INCREF(delay_cb);
    opq->delay = delay_cb;
#endif
    
    struct pam_conv conv = { &_pam_conversation, (void *)opq };
    pam_handle_t *handle;
    PAM_API(pam_start, service, user, &conv, &handle);
    if (self->rc == PAM_SUCCESS)
    {
        self->handle = handle;
    } else {
        Py_DECREF(e);
        return -1;
    }
    
    return 0;
}

static inline void _purge_sensitive(handle *self)
{
    if (geteuid() == 0 && self->flags & ctxflag_elevated)
    {
        // user with root access has chosen to view sensitive data,
        // don't blank it.
        return;
    }
#if HAS_PAM_UNSETENV
    pam_unsetenv(self->handle, "NTLMPWD");
    pam_unsetenv(self->handle, "mount_authenticator");
#endif
}

static inline int _handle_lock(handle *self, PyObject *exc)
{
    if (pthread_mutex_lock(&(self->lock)) != 0)
    {
        PyErr_SetFromErrno(exc);
        return 0;
    }
    return 1;
}

static inline int _handle_unlock(handle *self, PyObject *exc)
{
    if (pthread_mutex_unlock(&(self->lock)) != 0)
    {
        PyErr_SetFromErrno(exc);
        return 0;
    }
    return 1;
}

static PyObject *
handle_authenticate(handle *self, PyObject *args, PyObject *kws)
{
    int silent = 0;
    int disallow_nulltok = 0;
    static char *kwlist[] = {"silent", "disallow_null_token", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kws, "|ii", kwlist,
                                     &silent, &disallow_nulltok))
    {
        return NULL;
    }
    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }

    int flags = (silent) ?PAM_SILENT :0;
    flags |= (disallow_nulltok) ? PAM_DISALLOW_NULL_AUTHTOK :0;

    PAM_API(pam_authenticate, self->handle, flags);
    if (self->rc == PAM_SUCCESS)
    {
        _purge_sensitive(self);
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        Py_RETURN_TRUE;
    } else if (self->rc == PAM_AUTH_ERR) {
        _purge_sensitive(self);
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        Py_RETURN_FALSE;
    } else {
        int rc = self->rc;
        _purge_sensitive(self);
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        RAISE_PAM_ERR(self->handle, rc);
        return NULL;
    }
}

static inline int _handle_elevate(handle *self, PyObject *val)
{
    uid_t euid = geteuid();
    if (euid != 0)
    {
        int olderr = errno;
        errno = EACCES;
        PyErr_SetFromErrno(PyExc_OSError);
        errno = olderr;
        return -1;
    }
    self->flags ^= (-PyObject_IsTrue(val) ^ self->flags) & ctxflag_elevated;
    return 0;
}

static PyObject *
handle_acct_mgmt(handle *self, PyObject *args, PyObject *kws)
{
    int silent = 0;
    int disallow_nulltok = 0;
    static char *kwlist[] = {"silent", "disallow_null_token", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kws, "|ii", kwlist,
                                     &silent, &disallow_nulltok))
    {
        return NULL;
    }
    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }
    
    int flags = (silent) ?PAM_SILENT :0;
    flags |= (disallow_nulltok) ?PAM_DISALLOW_NULL_AUTHTOK :0;
    
    PAM_API(pam_acct_mgmt, self->handle, flags);
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
    if (self->rc != PAM_SUCCESS)
    {
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject *
handle_chauthtok(handle *self, PyObject *args, PyObject *kws)
{
    int silent = 0;
    int expired_only = 0;
    static char *kwlist[] = {"silent", "expired_only", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kws, "|ii", kwlist,
                                     &silent, &expired_only))
    {
        return NULL;
    }    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }

    int flags = (silent) ?PAM_SILENT :0;
    flags |= (expired_only) ?PAM_CHANGE_EXPIRED_AUTHTOK :0;

    PAM_API(pam_chauthtok, self->handle, flags);
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
    if (self->rc != PAM_SUCCESS)
    {
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    Py_RETURN_NONE;
}

#define CONTEXT_CRED_IMPL(flag) do { \
    int silent = 0; static char *kwlist[] = { "silent", NULL }; \
    if (!PyArg_ParseTupleAndKeywords(args, kws, "|i", kwlist, &silent)) \
    { return NULL; } \
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; } \
    int flags = flag | (silent) ?PAM_SILENT :0; \
    PAM_API(pam_setcred, self->handle, flags); \
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; } \
    if (self->rc != PAM_SUCCESS) { \
        RAISE_PAM_ERR(self->handle, self->rc); return NULL; \
    } \
    Py_RETURN_NONE; \
} while (0)

static PyObject *
handle_cred_est(handle *self, PyObject *args, PyObject *kws)
{
    CONTEXT_CRED_IMPL(PAM_ESTABLISH_CRED);
}

static PyObject *
handle_cred_del(handle *self, PyObject *args, PyObject *kws)
{
    CONTEXT_CRED_IMPL(PAM_DELETE_CRED);
}

static PyObject *
handle_cred_reinit(handle *self, PyObject *args, PyObject *kws)
{
    CONTEXT_CRED_IMPL(PAM_REINITIALIZE_CRED);
}

static PyObject *
handle_cred_refresh(handle *self, PyObject *args, PyObject *kws)
{
    CONTEXT_CRED_IMPL(PAM_REFRESH_CRED);
}

static PyObject *
handle_open_session(handle *self, PyObject *args, PyObject *kws)
{
    int silent = 0;

    static char *kwlist[] = {"silent", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kws, "|i", kwlist, &silent))
    {
        return NULL;
    }    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }

    int flags = (silent) ?PAM_SILENT :0;
    PAM_API(pam_open_session, self->handle, flags);
    if (self->rc != PAM_SUCCESS)
    {    
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    self->flags |= ctxflag_open_session;
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }

    Py_RETURN_NONE;
}

static PyObject *
handle_close_session(handle *self, PyObject *args, PyObject *kws)
{
    int silent = 0;

    static char *kwlist[] = {"silent", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kws, "|i", kwlist, &silent))
    {
        return NULL;
    }    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }

    int flags = (silent) ?PAM_SILENT :0;
    PAM_API(pam_close_session, self->handle, flags);
    if (self->rc != PAM_SUCCESS)
    {    
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    self->flags ^= ctxflag_open_session;
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }

    Py_RETURN_NONE;
}

#if HAS_PAM_FAIL_DELAY
static void _delay_fn(int retval, unsigned usec_delay, void *data)
{
    // PyObject *args;
    // args = Py_BuildValue("iIO", retval, usec_delay, (PyObject *)data);
    // void *adp;
    // opaque_data *opq;
    // int rc = pam_get_item(self->handle, PAM_CONV, (const void **)&adp);
    // if (rc != PAM_SUCCESS)
    // {
    //     return;
    // }
    // opq = (opaque_data *)()((struct pam_conv *)data)->appdata_ptr);
    // PyObject *cb = opq->delay;
    // PyObject *result = PyObject_CallObject(cb, args, NULL);
    // Py_XDECREF(result);
}

static PyObject *_delay_callback(PyObject *self, PyObject *args)
{
    Py_RETURN_NONE;
}

static PyObject *
handle_fail_delay(handle *self, PyObject *args, PyObject *kws)
{
    unsigned int usec;
    if (!PyArg_ParseTuple(args, "I", &usec))
    {
        return NULL;
    }    
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }
    PAM_API(pam_fail_delay, self->handle, usec);
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
    if (self->rc != PAM_SUCCESS)
    {
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    Py_RETURN_NONE;
}

#endif

static const int _pam_service = PAM_SERVICE;
static const int _pam_user = PAM_USER;
static const int _pam_tty = PAM_TTY;
static const int _pam_rhost = PAM_RHOST;
static const int _pam_ruser = PAM_RUSER;
static const int _pam_user_prompt = PAM_USER_PROMPT;
#if HAS_PAM_AUTHTOK
static const int _pam_authtok = PAM_AUTHTOK;
#endif
#if HAS_PAM_OLDAUTHTOK
static const int _pam_oldauthtok = PAM_OLDAUTHTOK;
#endif
#if HAS_PAM_AUTHTOK_PROMPT
static const int _pam_authtok_prompt = PAM_AUTHTOK_PROMPT;
#endif
#if HAS_PAM_OLDAUTHTOK_PROMPT
static const int _pam_oldauthtok_prompt = PAM_OLDAUTHTOK_PROMPT;
#endif
static const int _pam_conv = PAM_CONV;
#if HAS_PAM_FAIL_DELAY
static const int _pam_delay = PAM_FAIL_DELAY;
#endif

#define _PAM_DATA 2988
static const int _pam_data = _PAM_DATA;

#define _PAM_ELEVATE 2989
static const int _pam_elevated = _PAM_ELEVATE;

static PyObject *handle_getter(handle *self, void *key)
{
    int itype;
    itype = *(int *)key;
    const void *data;
    struct pam_conv *conv;
    opaque_data *opq;
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return NULL; }
    if (itype == _PAM_ELEVATE)
    {
        int elevated = (self->flags & ctxflag_elevated);
        if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
        if (elevated)
        {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    }
#if HAS_PAM_FAIL_DELAY
    if (itype == PAM_FAIL_DELAY)
    {
        PAM_API(pam_get_item, self->handle, PAM_CONV, &data);
    } else {
        PAM_API(pam_get_item, self->handle, itype, &data);
    }
#else
    PAM_API(pam_get_item, self->handle, itype, &data);
#endif
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return NULL; }
    if (self->rc != PAM_SUCCESS)
    {
        RAISE_PAM_ERR(self->handle, self->rc);
        return NULL;
    }
    switch (itype)
    {
        case PAM_SERVICE:
        case PAM_USER:
        case PAM_TTY:
        case PAM_RHOST:
        case PAM_RUSER:
        case PAM_USER_PROMPT:
#if HAS_PAM_AUTHTOK_PROMPT
        case PAM_AUTHTOK_PROMPT:
#endif
#if HAS_PAM_OLDAUTHTOK_PROMPT
        case PAM_OLDAUTHTOK_PROMPT:
#endif
#if HAS_PAM_AUTHTOK
        case PAM_AUTHTOK:
#endif
#if HAS_PAM_OLDAUTHTOK
        case PAM_OLDAUTHTOK:
#endif
        return Py_BuildValue("s", (char *)data);
        break;
        
        case PAM_CONV:
        conv = (struct pam_conv *)data;
        opq = (opaque_data *)(conv->appdata_ptr);
        return (PyObject *)(opq->conv);

#if HAS_PAM_FAIL_DELAY
        case PAM_FAIL_DELAY:
        conv = (struct pam_conv *)data;
        opq = (opaque_data *)(conv->appdata_ptr);
        return (PyObject *)(opq->delay);
#endif
        
        case _PAM_DATA:
        conv = (struct pam_conv *)data;
        opq = (opaque_data *)(conv->appdata_ptr);
        return (PyObject *)(opq->data);
    }
    Py_RETURN_NONE;
}

static int handle_setter(handle *self, PyObject *dataobj, void *key)
{
    int itype;
    itype = *(int *)key;
    if (dataobj == NULL
     && (itype != PAM_CONV
#if HAS_PAM_FAIL_DELAY
      && itype != PAM_FAIL_DELAY
#endif
      && itype != _PAM_DATA))
    {
        PyErr_SetString(PyExc_TypeError, "can't delete attribute");
        return -1;
    }
    struct pam_conv *conv;
    struct pam_conv _conv;
    opaque_data *opq;
    void *data;
    if (!_handle_lock(self, PyExc_EnvironmentError)) { return -1; }
    switch (itype)
    {
        case _PAM_ELEVATE:
        return _handle_elevate(self, dataobj);
        break;
        
        case PAM_SERVICE:
        case PAM_USER:
        case PAM_TTY:
        case PAM_RHOST:
        case PAM_RUSER:
        case PAM_USER_PROMPT:
#if HAS_PAM_AUTHTOK_PROMPT
        case PAM_AUTHTOK_PROMPT:
#endif
#if HAS_PAM_OLDAUTHTOK_PROMPT
        case PAM_OLDAUTHTOK_PROMPT:
#endif
#if HAS_PAM_AUTHTOK
        case PAM_AUTHTOK:
#endif
#if HAS_PAM_OLDAUTHTOK
        case PAM_OLDAUTHTOK:
#endif
        data = (void *)PyString_AsString(dataobj);
        break;
        
        case PAM_CONV:
        case _PAM_DATA:
#if HAS_PAM_FAIL_DELAY
        case PAM_FAIL_DELAY:
#endif
        PAM_API(pam_get_item, self->handle, PAM_CONV, (const void **)&data);
        if (self->rc != PAM_SUCCESS)
        {
            if (!_handle_unlock(self, PyExc_EnvironmentError)) { return -1; }
            RAISE_PAM_ERR(self->handle, self->rc);
            return -1;
        }
        conv = (struct pam_conv *)data;
        opq = (opaque_data *)malloc(sizeof(opaque_data));
        if (opq == NULL)
        {
            if (!_handle_unlock(self, PyExc_EnvironmentError)) { return -1; }
            PyErr_SetFromErrno(PyExc_SystemError);
            return -1;
        }
        opq->conv = ((opaque_data *)(conv->appdata_ptr))->conv;
#if HAS_PAM_FAIL_DELAY
        opq->delay = ((opaque_data *)(conv->appdata_ptr))->delay;
#endif
        opq->data = ((opaque_data *)(conv->appdata_ptr))->data;
        switch (itype)
        {
            case PAM_CONV:
            if (dataobj != NULL)
            {
                opq->conv = dataobj;
            } else {
                dataobj = PyObject_GetAttrString(_pam_module, "_conv_callback");
                opq->conv = dataobj;
            }
            break;
            
            case _PAM_DATA:
            if (dataobj != NULL)
            {
                opq->data = dataobj;
            } else {
                dataobj = Py_None;
                Py_INCREF(Py_None);
            }
            break;

#if HAS_PAM_FAIL_DELAY
            case PAM_FAIL_DELAY:
            if (dataobj != NULL)
            {
                opq->delay = dataobj;
            } else {
                dataobj = PyObject_GetAttrString(_pam_module, "_delay_callback");
                opq->conv = dataobj;
            }
            void (*ptr)(int, unsigned, void*) = &_delay_fn;
            pam_set_item(self->handle, PAM_FAIL_DELAY, (const void *)&ptr);
            break;
#endif
        }
        Py_INCREF(dataobj);
        _conv.conv = &_pam_conversation;
        _conv.appdata_ptr = (void *)opq;
        data = (void *)&_conv;
        itype = PAM_CONV;
        break;
    }
    
    PAM_API(pam_set_item, self->handle, itype, (const void *)data);
    if (!_handle_unlock(self, PyExc_EnvironmentError)) { return -1; }
    if (self->rc != PAM_SUCCESS)
    {
        RAISE_PAM_ERR(self->handle, self->rc);
        return -1;
    }
    return 0;
}

static PyMethodDef handle_methods[] = {
    {"authenticate", (PyCFunction)handle_authenticate, METH_KEYWORDS,
     "authenticate(silent=False, disallow_null_token=False) -> bool\n\n"
     "Authenticates the user associated with this handle."},
    {"acct_mgmt", (PyCFunction)handle_acct_mgmt, METH_KEYWORDS,
     "acct_mgmt(silent=False, disallow_null_token=False)\n\n"
     "Verifies and enforces account restrictions after the user has been\n"
     "authenticated."},
    {"change_token", (PyCFunction)handle_chauthtok, METH_KEYWORDS,
     "change_token(silent=False, change_expired=False)\n\n"
     "Changes the authentication token for the user associated with this handle."},
    {"establish_credentials", (PyCFunction)handle_cred_est, METH_KEYWORDS,
     "establish_credentials(silent=False)\n\n"
     "Establish the credentials of the target user."},
    {"delete_credentials", (PyCFunction)handle_cred_del, METH_KEYWORDS,
     "delete_credentials(silent=False)\n\n"
     "Revoke all established credentials."},
    {"reinitialize_credentials", (PyCFunction)handle_cred_reinit,
     METH_KEYWORDS,
     "reinitialize_credentials(silent=False)\n\n"
     "Fully reinitialize credentials."},
    {"refresh_credentials", (PyCFunction)handle_cred_refresh, METH_KEYWORDS,
     "refresh_credentials(silent=False)\n\n"
     "Refresh credentials."},
    {"open_session", (PyCFunction)handle_open_session, METH_KEYWORDS,
     "open_session(silent=False)\n\n"
     "Sets up a user session for a previously authenticated user."},
    {"close_session", (PyCFunction)handle_close_session, METH_KEYWORDS,
     "close_session(silent=False)\n\n"
     "Tears down a previously-established user session."},
#if HAS_PAM_FAIL_DELAY
    {"fail_delay", (PyCFunction)handle_fail_delay, METH_VARARGS,
     "fail_delay(usec)\n\n"},
#endif
    {NULL, NULL, 0, NULL}
};

static PyMemberDef handle_members[] = {
    {"environment", T_OBJECT_EX, offsetof(handle, environment), READONLY, ""},
    {NULL, 0, 0, 0, NULL}
};

#define CTX_ATTR(name, doc) \
{#name, (getter)handle_getter, (setter)handle_setter, doc, (void *)&_pam_##name}

static PyGetSetDef handle_getset[] = {
    CTX_ATTR(service, "The name of the requesting service."),
    CTX_ATTR(user, "The name of the user the application is trying to authenticate."),
    CTX_ATTR(tty, "The name of the current terminal."),
    CTX_ATTR(rhost, "The name of the applicant's host."),
    CTX_ATTR(ruser, "The name of the applicant."),
    CTX_ATTR(user_prompt, "The prompt to use when asking the applicant for a"
                          " user name\nto authenticate as."),
#if HAS_PAM_AUTHTOK_PROMPT
    CTX_ATTR(authtok_prompt, "The prompt to use when asking the applicant for"
                             " an authentiation token."),
#endif
#if HAS_PAM_OLDAUTHTOK_PROMPT
    CTX_ATTR(oldauthtok_prompt, "The prompt to use when asking the applicant"
                                " for an expired\nauthentication token prior"
                                " to changing it."),
#endif
#if HAS_PAM_AUTHTOK
    CTX_ATTR(authtok, "The current authentication token."),
#endif
#if HAS_PAM_OLDAUTHTOK
    CTX_ATTR(oldauthtok, "The expired authentication token."),
#endif
    CTX_ATTR(conv, "The current conversation callback."),
    CTX_ATTR(data, "Opaque data passed into callback functions."),
#if HAS_PAM_FAIL_DELAY
    CTX_ATTR(delay, "The current delay callback."),
#endif
    CTX_ATTR(elevated, "Whether this handle can perform arbitrator-level tasks."),
    {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject handleType = {
    PyObject_HEAD_INIT(NULL)
    /* ob_size */           0,
    /* tp_name */           "handle",
    /* tp_basicsize */      sizeof(handle),
    /* tp_itemsize */       0,
    /* tp_dealloc */        (destructor)handle_dealloc,
    /* tp_print */          0,
    /* tp_getattr */        0,
    /* tp_setattr */        0,
    /* tp_compare */        0,
    /* tp_repr */           0,
    /* tp_as_number */      0,
    /* tp_as_sequence */    0,
    /* tp_as_mapping */     0,
    /* tp_hash */           0,
    /* tp_call */           0,
    /* tp_str */            0,
    /* tp_getattro */       0,
    /* tp_setattro */       0,
    /* tp_as_buffer */      0,
    /* tp_flags */          Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    /* tp_doc */            "handle objects",
    /* tp_traverse */       0,
    /* tp_clear */          0,
    /* tp_richcompare */    0,
    /* tp_weaklistoffset */ 0,
    /* tp_iter */           0,
    /* tp_iternext */       0,
    /* tp_methods */        handle_methods,
    /* tp_members */        handle_members,
    /* tp_getset */         handle_getset,
    /* tp_base */           0,
    /* tp_dict */           0,
    /* tp_descr_get */      0,
    /* tp_descr_set */      0,
    /* tp_dictoffset */     0,
    /* tp_init */           (initproc)handle_init,
    /* tp_alloc */          PyType_GenericAlloc,
    /* tp_new */            PyType_GenericNew,
    /* tp_free */           0,
    /* tp_is_gc */          0,
    /* tp_bases */          0,
    /* tp_mro */            0,
    /* tp_cache */          0,
    /* tp_subclasses */     0,
    /* tp_weaklist */       0,
    /* tp_del */            0,
    /* tp_version_tag */    0,
};

#pragma endregion -

#pragma region module implementation

static PyMethodDef _pam_module_methods[] = {
    {"_conv_callback", (PyCFunction)_conv_callback, METH_VARARGS, ""},
#if HAS_PAM_FAIL_DELAY
    {"_delay_callback", (PyCFunction)_delay_callback, METH_VARARGS, ""},
#endif
    {NULL, NULL, 0, NULL}
};

static inline void _populate_retcodes(void)
{
    PAM_DEFINE(pam_rc_abort, PAM_ABORT);
    PAM_DEFINE(pam_rc_acct_exp, PAM_ACCT_EXPIRED);
    PAM_DEFINE(pam_rc_authinfo_unavail, PAM_AUTHINFO_UNAVAIL);
    PAM_DEFINE(pam_rc_authtok_disage, PAM_AUTHTOK_DISABLE_AGING);
    PAM_DEFINE(pam_rc_authtok_err, PAM_AUTHTOK_ERR);
    PAM_DEFINE(pam_rc_authtok_exp, PAM_AUTHTOK_EXPIRED);
    PAM_DEFINE(pam_rc_authtok_busy, PAM_AUTHTOK_LOCK_BUSY);
    PAM_DEFINE(pam_rc_authtok_recerr, PAM_AUTHTOK_RECOVERY_ERR);
    PAM_DEFINE(pam_rc_auth_err, PAM_AUTH_ERR);
    PAM_DEFINE(pam_rc_buf_err, PAM_BUF_ERR);
    PAM_DEFINE(pam_rc_conv_err, PAM_CONV_ERR);
    PAM_DEFINE(pam_rc_cred_err, PAM_CRED_ERR);
    PAM_DEFINE(pam_rc_cred_exp, PAM_CRED_EXPIRED);
    PAM_DEFINE(pam_rc_cred_insuff, PAM_CRED_INSUFFICIENT);
    PAM_DEFINE(pam_rc_cred_unavail, PAM_CRED_UNAVAIL);
#if !IMPL_LINUX_PAM
    PAM_DEFINE(pam_rc_domain_unk, PAM_DOMAIN_UNKNOWN);
#endif
    PAM_DEFINE(pam_rc_ignore, PAM_IGNORE);
    PAM_DEFINE(pam_rc_maxtries, PAM_MAXTRIES);
    PAM_DEFINE(pam_rc_module_unk, PAM_MODULE_UNKNOWN);
    PAM_DEFINE(pam_rc_new_authtok_req, PAM_NEW_AUTHTOK_REQD);
    PAM_DEFINE(pam_rc_no_module_data, PAM_NO_MODULE_DATA);
    PAM_DEFINE(pam_rc_open_err, PAM_OPEN_ERR);
    PAM_DEFINE(pam_rc_perm_denied, PAM_PERM_DENIED);
    PAM_DEFINE(pam_rc_service_err, PAM_SERVICE_ERR);
    PAM_DEFINE(pam_rc_session_err, PAM_SESSION_ERR);
    PAM_DEFINE(pam_rc_success, PAM_SUCCESS);
    PAM_DEFINE(pam_rc_symbol_err, PAM_SYMBOL_ERR);
    PAM_DEFINE(pam_rc_system_err, PAM_SYSTEM_ERR);
    PAM_DEFINE(pam_rc_try_again, PAM_TRY_AGAIN);
    PAM_DEFINE(pam_rc_user_unk, PAM_USER_UNKNOWN);
}

PyMODINIT_FUNC
initpam(void)
{
    if (PyType_Ready(&handleType) < 0
     || PyType_Ready(&environmentType) < 0
     || PyType_Ready(&environment_iterType) < 0)
    {
        return ;
    }
    
    _pam_module = Py_InitModule("pam", _pam_module_methods);
    if (_pam_module == NULL) { return; }
    
    PamError = PyErr_NewExceptionWithDoc("pam.PamError",
        "Wrapper class for errors which occur in the PAM library.",
        PyExc_EnvironmentError, NULL);
    Py_INCREF(PamError);
    PyModule_AddObject(_pam_module, "PamError", PamError);
    
    Py_INCREF(&handleType);
    PyModule_AddObject(_pam_module, "handle", (PyObject *)&handleType);
#if HAS_FROZENSET
    PyObject *exts = PyFrozenSet_New(NULL);
#else
    PyObject *exts = PySet_New(NULL);   // PyPy doesn't support frozenset()?
#endif
    if (exts == NULL) { return; }
    
    _gp_module = PyImport_ImportModule("getpass");
    if (_gp_module == NULL) { return; }
    _gp_fn = PyObject_GetAttrString(_gp_module, "getpass");
    if (_gp_fn == NULL) { return; }

#if IMPL_OPENPAM
    PyModule_AddStringConstant(_pam_module, "implementation", "OpenPAM");
#elif IMPL_LINUX_PAM
    PyModule_AddStringConstant(_pam_module, "implementation", "Linux-PAM");
#else
    PyModule_AddStringConstant(_pam_module, "implementation", "?");
#endif
#if HAS_PAM_UNSETENV
    PySet_Add(exts, Py_BuildValue("s", "unsetenv"));
#endif
#if HAS_PAM_FAIL_DELAY
    PySet_Add(exts, Py_BuildValue("s", "fail_delay"));
#endif
    Py_INCREF(exts);
    PyModule_AddObject(_pam_module, "extensions", exts);
    
    _populate_retcodes();
    _populate_styles();
}

#pragma endregion

