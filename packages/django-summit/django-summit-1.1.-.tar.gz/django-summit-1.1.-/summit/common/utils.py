import email
import os

from django.conf import settings


def redirect(to, *args, **kwargs):
    from distutils.version import LooseVersion as V
    import django
    if V(django.get_version()) > V('1.1'):
        from django.shortcuts import redirect as red
    else:
        from shortcuts import redirect as red

    return red(to, *args, **kwargs)


def get_summit_version(version_file, debug):
    """
    return the bzr revision number and version of The Summit Scheduler
    """

    if not os.path.exists(version_file):
        return "version unknown"

    f = email.message_from_file(open(version_file))
    version = f["version"]
    bzr_revno = f["revno"]
    
    if debug:
        try:
            from bzrlib.branch import Branch
            branch = Branch.open_containing('.')[0]
            bzr_revno = branch.revno()
        except:
            pass

    return "version %s (rev %s)" % (version, bzr_revno)
