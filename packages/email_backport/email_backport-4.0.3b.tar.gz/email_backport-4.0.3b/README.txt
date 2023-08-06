5A5AThe email_backport package is a wrap-up of the email > 4.x module
found in Python 2.5 and above.

This is to create a simple way of creating email-related code that
works with existing Python code and interpreters (>= Python 2.3) as
there has been a lot of changes such as new naming standards, see
here:

  http://docs.python.org/library/email

To use in your code, try something like:

EMAIL_4 = False
import sys
try:
    from email import message
    EMAIL_4 = True
except ImportError:
    sys._IMPORTING_EMAIL_BACKPORT = True
    try:
        import email_backport as email
        sys.modules['email'] = email
        EMAIL_4 = True
    except ImportError:
        EMAIL_4 = False

If EMAIL_4 is true, we're good to go, if not, one can disable mail
features of the application.

The versioning of email_backport follows Python's email module
internal version.

You can find the SVN version of this package here:

  https://svn.nidelven-it.no/svn/shared-pypi-modules/

Login is svnaccess/svnaccess (read-only access).  If you want to
contribute, drop us a line!
