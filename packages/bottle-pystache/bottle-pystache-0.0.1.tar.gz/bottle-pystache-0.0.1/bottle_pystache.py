import functools
import threading

import bottle

__all__ = ['PystacheTemplate', 'view']

class PystacheTemplate(bottle.BaseTemplate):
    ''' Pystache is a Python Mustache implementation.
        Set `View.template_extension` to be able to use partials,
        because partial calls are not handled by Bottle and Pystache works
        with only one extension, defined as `mustache` by default.
    '''

    try:
        extensions = bottle.BaseTemplate.extensions
    except AttributeError:
        # Bottle had a misspelling in BaseTemplate.
        # It is fixed in Bottle v0.10.
        extensions = bottle.BaseTemplate.extentions
    extensions.insert(0, 'mustache')

    def prepare(self, **options):
        from pystache import Renderer
        self.context = threading.local()
        self.context.vars = {}
        self.tpl = Renderer(search_dirs=self.lookup, **options)

    def render(self, *args, **kwargs):
        for dictarg in args:
            kwargs.update(dictarg)

        kwargs.update(self.defaults)
        out = self.tpl.render_path(self.filename, **kwargs)
        return out

view = functools.partial(bottle.view, template_adapter=PystacheTemplate)

