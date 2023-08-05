# -*- coding: utf-8 -*-
"""
    blohg.mercurial_theme
    ~~~~~~~~~~~~~~~~~~~~~

    Module with the stuff needed by blohg to use Jinja2 templates and
    static files from the Mercurial repository.

    :copyright: (c) 2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import current_app, g, request, abort
from jinja2.loaders import BaseLoader, ChoiceLoader, TemplateNotFound, \
    split_template_path
from time import time
from zlib import adler32

import posixpath
import mimetypes


def setup_theme(app):
    """This function replaces the default jinja loader from flask with
    a ChoiceLoader, that tries to load templates from the mercurial
    repository and fallback to the default jinja loader. This function
    also replace the static url endpoint by another, that load files
    from the mercurial repository as well.

    :param app: the application object.
    """

    old_loader = app.jinja_loader
    app.jinja_loader = ChoiceLoader([
        MercurialLoader(),
        old_loader,
    ])
    app.add_url_rule(
        app.static_url_path + '/<path:filename>',
        endpoint='static',
        view_func=MercurialStaticFile(app.config['STATIC_DIR'])
    )
    app.add_url_rule(
        '/attachments/<path:filename>',
        endpoint='attachments',
        view_func=MercurialStaticFile(app.config['ATTACHMENT_DIR'])
    )


class MercurialLoader(BaseLoader):
    """A Jinja2 loader that loads templates from a Mercurial repository"""

    def _filerev(self, filectx):
        filelog = filectx.filelog()
        revision_list = list(filelog)
        if len(revision_list) == 0:
            revision_id = 0
        else:
            revision_id = revision_list[-1]
        return filelog.linkrev(revision_id)

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        templates_dir = current_app.config['TEMPLATES_DIR']
        filename = posixpath.join(templates_dir, *pieces)
        if filename in list(current_app.hg.revision):
            filectx = current_app.hg.revision[filename]
            contents = filectx.data().decode('utf-8')
            revision = self._filerev(filectx)
            def up2date():
                if g is None or g.repo.rev() is None or revision == -1:
                    return False
                return revision >= self._filerev(g.repo[filename])
            return contents, filename, up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = current_app.config['TEMPLATES_DIR']
        return sorted([i for i in current_app.hg.revision \
            if i.startswith(templates_dir + '/')])


class MercurialStaticFile(object):
    """Callable to create a Response object for static files loaded from
    the current Mercurial repository.
    """

    def __init__(self, directory):
        self._directory = directory

    def __call__(self, filename):
        filename = posixpath.join(self._directory, filename)
        mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            mimetype = 'application/octet-stream'
        try:
            filectx = current_app.hg.revision[filename]
            data = filectx.data()
        except:
            abort(404)
        rv = current_app.response_class(data, mimetype=mimetype,
            direct_passthrough=True)
        rv.cache_control.public = True
        cache_timeout = 60 * 60 * 12
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time() + cache_timeout)
        try:
            date = int(filectx.date()[0])
        except:
            date = time()
        rv.set_etag('blohg-%s-%s-%s' % (date, len(data), adler32(filename) \
            & 0xffffffff))
        return rv.make_conditional(request)
