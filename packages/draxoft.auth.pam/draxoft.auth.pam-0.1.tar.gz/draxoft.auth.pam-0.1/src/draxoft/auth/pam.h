#ifndef PAM_H_7BT2F1QZ
#define PAM_H_7BT2F1QZ

#include <sys/types.h>
#include <unistd.h>
#include <termios.h>
#include <pwd.h>
#include <security/pam_appl.h>

/* implementation */
#define IMPL_OPENPAM 0
#define IMPL_LINUX_PAM 0

/* features */
#define HAS_PAM_AUTHTOK_PROMPT 0
#define HAS_PAM_OLDAUTHTOK_PROMPT 0
#define HAS_PAM_AUTHTOK 0
#define HAS_PAM_OLDAUTHTOK 0

#define HAS_PAM_UNSETENV 0

#define HAS_PAM_FAIL_DELAY 0

#define ENVIRON_REPR_OPAQUE 1

#ifdef OPENPAM

    #include <security/openpam.h>
    #undef IMPL_OPENPAM
    #define IMPL_OPENPAM 1
    
    #undef HAS_PAM_AUTHTOK_PROMPT
    #undef HAS_PAM_OLDAUTHTOK_PROMPT
    #undef HAS_PAM_AUTHTOK
    #undef HAS_PAM_OLDAUTHTOK
    #define HAS_PAM_AUTHTOK_PROMPT 1
    #define HAS_PAM_OLDAUTHTOK_PROMPT 1
    #define HAS_PAM_AUTHTOK 1
    #define HAS_PAM_OLDAUTHTOK 1
    
    #undef HAS_PAM_UNSETENV
    #define HAS_PAM_UNSETENV 1
    
#elif defined(__LINUX_PAM__)

    #include <security/pam_ext.h>
    #undef IMPL_LINUX_PAM
    #define IMPL_LINUX_PAM 1
    
#else

    #if defined(HAVE_PAM_FAIL_DELAY)
    #undef HAS_PAM_FAIL_DELAY
    #define HAS_PAM_FAIL_DELAY 1
    #endif

#endif


#define RAISE_PAM_ERR(hdl, rc) do { \
PyErr_SetObject(PamError, Py_BuildValue("(is)", rc, pam_strerror(hdl, rc))); \
} while (0)

#endif /* end of include guard: PAM_H_7BT2F1QZ */
