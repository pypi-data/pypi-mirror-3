from paste.script.templates import Template, var
from paste.script.util.secret import secret_string
from paste.deploy.converters import asbool

from tempita import paste_script_template_renderer

class FlaskSkelTemplate(Template):
    """
    Default flaskskel template
    """
    _template_dir = 'templates/default_project'
    required_templates = []
    template_renderer = staticmethod(paste_script_template_renderer)
    
    summary = 'Flask Skel template'
    vars = [
        var('flask_project_name',
            'Name of the main Flask project folder',
            default='project')
    ]


    def pre(self, command, output_dir, vars):

        vars['secret_key'] = secret_string()
