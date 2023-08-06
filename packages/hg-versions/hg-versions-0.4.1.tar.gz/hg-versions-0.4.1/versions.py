# versions.py
#
# Copyright 2010 Markus Zapke-Gruendemann <info@keimlink.de>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""display the version information for Mercurial and all installed extensions"""

from mercurial import commands, extensions, util
from mercurial.i18n import _

__version__ = '0.4.1'

def get_extension_version(name):
    """Gets the version information for an extension.

    This code was inspired by Django Debug Toolbar's VersionDebugPanel.
    """
    extension = extensions.find(name)
    if hasattr(extension, 'get_version'):
        get_version = extension.get_version
        if callable(get_version):
            version = get_version()
        else:
            version = get_version
    elif hasattr(extension, 'VERSION'):
        version = extension.VERSION
    elif hasattr(extension, '__version__'):
        version = extension.__version__
    else:
        version = ''
    if isinstance(version, (list, tuple)):
        version = '.'.join(str(o) for o in version)
    return version

def versions(ui, **opts):
    """display the version information for Mercurial and all installed extensions

    Displays only extensions with a version by default.
    """
    versions = {}
    for name, module in ui.configitems('extensions'):
        try:
            versions[name] = get_extension_version(name)
        except KeyError:
            pass
    ui.write(_('Mercurial version: %s\n\n') % util.version())
    ui.write(_('enabled extensions:\n\n'))
    for item in sorted(versions.iteritems()):
        if not opts.get('all') and len(item[1]) == 0:
            continue
        ui.write(' %s %s\n' % item)

cmdtable = {'versions':
    (versions, [('a', 'all', None, _('Display all extensions'))], '[-a]')}

commands.norepo += ' versions'
