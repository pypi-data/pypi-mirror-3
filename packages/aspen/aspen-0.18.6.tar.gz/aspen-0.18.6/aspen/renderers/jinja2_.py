from aspen.rendering import Renderer, Factory

from jinja2 import BaseLoader, TemplateNotFound, Environment, FileSystemLoader, Template

def no():
    return False # Jinja2 asks the given function if template should be reloaded, default is always

class SimplateLoader(BaseLoader):
    
    def get_source(self, environment, template):
        return (unicode(open("root/%s" % template).read(), 'utf-8'), template, no)
    
    def load(self, environment, name, globals=None):
        if not globals.has_key("raw"):
            return super(SimplateLoader, self).load(environment, name, globals)
        else:
            code = environment.compile(globals["raw"].decode("utf-8"), name, name)
            return environment.template_class.from_code(environment, code,
                                                    globals, no)

class Jinja2Renderer(Renderer):
    
    def compile(self, filepath, raw):
        return self.meta.get_template(filepath, globals={"raw":raw})

    def render_content(self, compiled, context):
        return compiled.render(context).encode("utf-8")

class Jinja2Factory(Factory):

    Renderer = Jinja2Renderer

    def __init__(self, configuration):
        self.env = Environment(loader = SimplateLoader())
        super(Jinja2Factory, self).__init__(configuration)

    def compile_meta(self, configuration):
        return self.environment
