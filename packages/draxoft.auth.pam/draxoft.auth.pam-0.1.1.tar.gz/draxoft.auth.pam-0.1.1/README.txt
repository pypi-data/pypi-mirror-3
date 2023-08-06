draxoft.auth.pam v0.1.1
=======================

Provides a Python-style interface to PAM's C API.

This module supports the POSIX interface to PAM, as well as many of the
extensions provided by **Linux-PAM** and **OpenPAM**.

Compatibility Notes
-------------------

 * There is an issue with the constructor under PyPy: if an AttributeError is
   raised, try calling it as ``pam.handle(conv=pam._conv_callback)``.