:mod:`draxoft.auth.pam`
=======================

.. module:: draxoft.auth.pam

.. toctree::
   :maxdepth: 2

This module provides a Python-style interface to PAM's C API; all
functionality is exposed through the :obj:`handle` class and its instances.

.. class:: handle(**parameters)
   
   Represents a PAM handle.

   The `parameters` have the same names as the instance attributes:

      .. attribute:: service
      
         Specifies the PAM service module used.

      .. attribute:: user
      
         Associates this :obj:`handle` with a specific user.

      .. attribute:: conv
                     delay
         :noindex:
            
         Allows specifying callbacks; see below (:attr:`conv`, :attr:`delay`).

      .. attribute:: data
      
         Opaque data passed to any associated callback functions.

Authentication
--------------

.. automethod:: handle.authenticate

   >>> from draxoft.auth import pam
   >>> import random
   >>> c = pam.handle()
   >>> c.user = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 7))
   >>> c.user # doctest: +SKIP
   fbvqrpo
   >>> c.conv = lambda style,msg,data: 'password'
   >>> c.authenticate()
   Traceback (most recent call last):
      ...
   pam.PamError: [Errno 13] unknown user
   >>> try:
   ...     c.authenticate()
   ... except pam.PamError, e:
   ...     e.errno == pam.PAM_USER_UNKNOWN
   True

.. attribute:: handle.conv

   :signature: :samp:`callback({style}, {message}, {data})`

   Conversation callback. Provides a conversation callback for retrieving user
   IDs and authentication tokens.

   Defaults to :meth:`_conv_callback`.

Account management
------------------

.. automethod:: handle.acct_mgmt

Credential management
---------------------

.. automethod:: handle.establish_credentials

.. automethod:: handle.delete_credentials

.. automethod:: handle.reinitialize_credentials

.. automethod:: handle.refresh_credentials

Session management
------------------

.. automethod:: handle.open_session

.. automethod:: handle.close_session

Environment
-----------

.. attribute:: handle.environ
   
   Mapping from environment variable names to values, both strings.
   
   .. warning::
   
      **Direct references to this object are unsafe!** Do not assign it to a
      variable or in any other way store its value without a copy operation.
      
      The implementation of this object is closely linked with that of the
      parent :obj:`handle` in a way that creates circular references. As a
      result, no reference is stored for the parent object -- which means a
      reference to an :attr:`environ` attribute could well access reclaimed
      memory when used or garbage collected, potentially causing a crash.
      
      This should be considered a bug and will be fixed "Real Soon Now."
   
   If the ``'unsetenv'`` :attr:`extension <extensions>` is provided, variables
   may be removed using the ``del`` operator.
   
   >>> ctx = pam.handle()
   >>> ctx.environ['answer'] = 42   # the input can be a Python object...
   >>> ctx.environ['answer']        # ...but the output will be a string.
   '42'
   >>> if 'unsetenv' in pam.extensions:
   ...     del ctx.environ['answer']
   ...     'answer' not in ctx.environ
   ... else:
   ...     'answer' in ctx.environ
   ...
   True

.. attribute:: handle.elevated
   
   The :attr:`environ` attribute may contain sensitive information,
   particularly after a call to :meth:`authenticate`. By default, this
   information will be removed. If this module is being run effective-user-ID
   0, this attribute can be set to :obj:`True` to prevent this scrubbing.
   
   >>> ctx = pam.handle()
   >>> ctx.elevated
   False
   >>> ctx.elevated = True
   Traceback (most recent call last):
      ...
   OSError: [Errno 13] Permission denied
   

Fail delay
----------

Only supported/defined if ``'fail_delay'`` in :obj:`extensions`.

.. warning::
   
   **The fail delay API is experimental and poorly tested.**
   
   The :attr:`.delay` callback currently does nothing; :meth:`.fail_delay`
   *should* work correctly.
   
   The author expects a complete implementation of :attr:`.delay` by v0.2,
   hopefully by v0.1.2. Any testing or bug reports would be greatly
   appreciated...

.. seealso::
   
   ``pam_fail_delay(3)``
      PAM **man** page describing the fail delay API in more detail.

.. method:: handle.fail_delay(usec)

   Provides a mechanism by which an application can suggest a minimum delay
   of `usec` microseconds.

   The handle records the longest time requested; should :meth:`authenticate`
   fail, the return to the application is delayed by an amount of time
   randomly distributed (by up to 25%) about this longest value.

.. attribute:: handle.delay

   :signature: :samp:`callback({rc}, {usec}, {data})`

   This callback allows an application to control the mechanism by which the
   PAM fail delay is implemented.

   For some applications, a blocking delay between failure and return may be
   unacceptable. Single-threaded server applications, for example, might
   prefer to block just the client's queued requests instead of the server
   itself.

   The `rc` argument is the last return code; `usec` is the requested delay
   (in microseconds) and `data` is the opaque :attr:`data`.

   The default is :obj:`None`, in which case fail delay (if any) is entirely
   controlled by the :meth:`fail_delay` method.

Errors
------

.. exception:: PamError

   Base class: :exc:`~exceptions.EnvironmentError`

   Wrapper class for errors occurring in the PAM library. Nearly every
   :obj:`handle` method or property may raise these in event of an internal
   error.

   .. attribute:: strerror
      
      Describes the error "in plain English" suitable for display.

   .. attribute:: errno

      One of the :ref:`error-codes` listed below. Unfortunately,
      this value is an integer and therefore may carry little meaning for the
      recipient.

      .. _error-codes:
   
      .. table:: **error codes**

         =================================== ===========
         Error                               Description
         =================================== ===========
         .. data:: PAM_ABORT                 General failure.
         .. data:: PAM_ACCT_EXPIRED          User account has expired.
         .. data:: PAM_AUTHINFO_UNAVAIL      Authentication information is
                                             unavailable.
         .. data:: PAM_AUTHTOK_DISABLE_AGING Authentication token aging
                                             disabled.
         .. data:: PAM_AUTHTOK_ERR           Authentication token failure.
         .. data:: PAM_AUTHTOK_EXPIRED       Password has expired.
         .. data:: PAM_AUTHTOK_LOCK_BUSY     Authentication token lock busy.
         .. data:: PAM_AUTHTOK_RECOVERY_ERR  Failed to recover old
                                             authentication token.
         .. data:: PAM_AUTH_ERR              Authentication error.
         .. data:: PAM_BUF_ERR               Memory buffer error.
         .. data:: PAM_CONV_ERR              Conversation error.
         .. data:: PAM_CRED_ERR              Failed to set user credentials.
         .. data:: PAM_CRED_EXPIRED          User credentials have expired.
         .. data:: PAM_CRED_INSUFFICIENT     Insufficient credentials.
         .. data:: PAM_CRED_UNAVAIL          Failed to retrieve user
                                             credentials.
         .. data:: PAM_DOMAIN_UNKNOWN        Unknown authentication domain.
         .. data:: PAM_IGNORE                Ignore this module.
         .. data:: PAM_MAXTRIES              Maximum number of tries exceeded.
         .. data:: PAM_MODULE_UNKNOWN        Unknown module type.
         .. data:: PAM_NEW_AUTHTOK_REQD      New authentication token
                                             required.
         .. data:: PAM_NO_MODULE_DATA        Module data not found.
         .. data:: PAM_OPEN_ERR              Failed to load module.
         .. data:: PAM_PERM_DENIED           Permission denied.
         .. data:: PAM_SERVICE_ERR           Error in service module.
         .. data:: PAM_SESSION_ERR           Session failure.
         .. data:: PAM_SUCCESS               Success.
         .. data:: PAM_SYMBOL_ERR            Invalid symbol.
         .. data:: PAM_SYSTEM_ERR            System error.
         .. data:: PAM_TRY_AGAIN             Try again.
         .. data:: PAM_USER_UNKNOWN          Unknown user.
         =================================== ===========

Extensions
----------

.. attribute:: implementation
   
   Specifies the PAM implementation, if known.
   
   ================= ==============
   Platform          Implementation
   ================= ==============
   AIX 4.3 (patched) ``'Linux-PAM'``
   AIX 5.1 (ML01+)   ``'?'``
   AIX 5.2+          ``'?'``
   Darwin (Mac OS X) ``'OpenPAM'``
   DragonflyBSD      ``'OpenPAM'``
   FreeBSD           ``'OpenPAM'``
   HP-UX             ``'?'``
   Linux             ``'Linux-PAM'`` (some distros support ``'OpenPAM'``)
   NetBSD            ``'OpenPAM'``
   PC-BSD            ``'OpenPAM'``
   Solaris           ``'OpenPAM'``
   ================= ==============

.. attribute:: extensions
   
   Set of strings describing the API extensions supported by this module.
   Potential extensions include:
   
      ``'fail_delay'``
         This module supports the PAM fail delay API. Currently only provided
         by **Linux-PAM** implementations.
   
      ``'unsetenv'``
         Environment variables can be deleted in this implementation.
         Currently only supported by **OpenPAM**.
