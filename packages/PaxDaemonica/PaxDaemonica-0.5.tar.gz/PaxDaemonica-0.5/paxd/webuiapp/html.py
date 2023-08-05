import os
from paxd import PROJECT_PATH
import mako
from mako.lookup import TemplateLookup

def render(path, context):
    lookup = TemplateLookup(directories=[os.path.join(PROJECT_PATH, 'paxd/webuiapp/templates')])
    template = lookup.get_template(path)
    try:
        return template.render_unicode(**context)
    except:
        return mako.exceptions.html_error_template().render()
    
