from Products.Archetypes.Extensions.utils import install_subskin
from Products.PloneContentTemplates.config import GLOBALS
from cStringIO import StringIO

def install(self):
    out = StringIO()
    install_subskin(self, out, GLOBALS)
    out.write('Installed skin')
    return out.getvalue()