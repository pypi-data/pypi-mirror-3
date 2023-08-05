# -*- coding: utf-8 -*-
"""
    flaskext.breve
    ~~~~~~~~~~~~~~
    
    Usage::
        
        from flaskext.breve import Breve, render_template
        breve = Breve(some_flask_app)
        
    Now::
        
        render_template('admin/index', context={})
    
    renders the file 'index.b' in the admin module's template directory.

    :copyright: (c) 2010 by Daniel Gerber.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement, absolute_import
import os.path
from functools import wraps
from werkzeug import cached_property
import flask
from flask.signals import template_rendered
import breve
from breve.tags import html as xhtml, html4


class _LoaderAdapter(object):
    
    def __init__(self, jinja_loader):
        self.jinja_loader = jinja_loader
    
    def stat(self, template, root):
        uid = '%s%s' % (root or '', template)
        s, fname, u = self.jinja_loader.get_source(None, uid)
        return uid, os.path.getmtime(fname)
    
    def load(self, uid):
        return self.jinja_loader.get_source(None, uid)[0]


#: Named configurations for Template instantiation and rendering
methods = {
    'xhtml': {
            'xml_encoding': '<?xml version="1.0" encoding="UTF-8"?>',#XML Decl.
            'doctype': xhtml.doctype, # Doctype Decl.
            'xmlns': xhtml.xmlns, 
            'tags': xhtml.tags}, 
    '(x)html': {
            'xml_encoding': '',
            'doctype': '<!DOCTYPE html>', 
            'xmlns': 'http://www.w3.org/1999/xhtml', 
            'tags': xhtml.tags},
    'html': {
            'xml_encoding': '',#XML Decl.
            'doctype': html4.doctype, # Doctype Decl.
            'xmlns': html4.xmlns, 
            'tags': html4.tags}
    }


for k in ['url_for', 'get_flashed_messages']:
    breve.register_global(k, getattr(flask, k))


class Breve(object):
    
    default_options = dict(
        #: extension for template file names
        #: breve adds a dot in any case
        extension = 'b', 
        
        #: XML declaration string
        xml_encoding = '', 
        #: Doctype declaration string
        doctype = '<!DOCTYPE html>', 
        xmlns = 'http://www.w3.org/1999/xhtml', 
        tags = xhtml.tags, 
        
        namespace = None, 
        root = None
    )
    
    def __init__(self, app, default_method='(x)html', **options):
        app.breve_instance = self
        self.app = app
        
        self.options = self.default_options.copy()
        self.options.update(methods[default_method])
        self.options.update(options)
#        try:
#            self.inject_babel()
#        except:
#            pass
#    
#    def inject_babel(self):
#        from flaskext.babel import gettext, _, ngettext
#        self.app.context_processor(lambda: {
#                    'gettext': gettext, '_': _, 'ngettext': ngettext})

    @cached_property
    def template_loader(self):
        return _LoaderAdapter(self.app.jinja_env.loader)


def render_template(template_name=None, context=None, format=None, **options):
    u"""Renders a Brevé template.
    
    :param template_name: as in `flask.render_template` but *without extension*.
    :param context: a dict of context variables
    :param **options: passed on to `breve.Template`.
    """
    app = flask.current_app
    if context is None:
        context = {}
    app.update_template_context(context)
    
    bi = app.breve_instance
    for k, v in bi.options.iteritems():
        options.setdefault(k, v)
    
    template = breve.Template(**options)
    rt = template.render(template_name, vars=context, 
                                    loader=bi.template_loader, format=format)
    template_rendered.send(app, template=template, context=context)
    return rt


def flattened_by(method_name):
    """Class decorator to register the named method as flattener.
    
    Example use::
    
        @flattened_by('__html__')
        class C:
            def __html__(self):
                return '<div>%s</div>' % self
    """
    def decorator(cls):
        breve.register_flattener(cls, getattr(cls, method_name))
        return cls
    return decorator


def templated(name=None):
    """Decorator for view functions.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            template_name = name if name is not None else\
                    flask.request.endpoint.replace('.', '/')
            return render_template(template_name, context=ctx)
        return decorated
    return decorator
