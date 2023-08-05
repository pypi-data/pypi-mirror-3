import inspect
import os
from collections import defaultdict
from StringIO import StringIO

from pkg_resources import resource_string

web_xml_defaults = defaultdict(str)
web_xml_defaults.update(log_level='info')

def gen_web_xml(**options):
    """Generate a deployment descriptor (web.xml)"""
    vars = web_xml_defaults.copy()
    vars.update(options)
    tmpl = os.path.join('war_template', 'WEB-INF', 'web.xml_tmpl')
    return resource_string('snakefight', tmpl) % vars

def gen_paste_loadapp(config, app_name):
    """Generate a .py module with a loadapp() callable that loads the
    Paste app via config"""
    code = StringIO()
    code.write("""\
# as located in WEB-INF
config = '%s'
app_name = '%s'

""" % (config, app_name))
    code.write(inspect.getsource(loadapp))
    return code.getvalue()

# loadapp exists only to be inspect.getsource'd
def loadapp():
    """Load a WSGI app from a Paste config file in WEB-INF"""
    import os
    import paste.deploy
    config_dir = os.path.normpath(__file__)
    for i in range(2):
        config_dir = os.path.dirname(config_dir)
    return paste.deploy.loadapp('config:%s#%s' %
                                (os.path.join(config_dir, config), app_name))
