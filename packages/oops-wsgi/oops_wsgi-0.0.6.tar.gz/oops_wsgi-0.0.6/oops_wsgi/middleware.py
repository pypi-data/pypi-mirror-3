# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Affero General Public License version 3 (see the file LICENSE).

"""WSGI middleware to integrate with an oops.Config."""

__metaclass__ = type

import socket
import sys

from paste.request import construct_url

__all__ = [
    'default_map_environ',
    'generator_tracker',
    'make_app',
    ]


default_error_template='''<html>
<head><title>Oops! - %(id)s</title></head>
<body>
<h1>Oops!</h1>
<p>Something broke while generating the page.
Please try again in a few minutes, and if the problem persists file
a bug or contact customer support. Please quote OOPS-ID
<strong>%(id)s</strong>
</p></body></html>'''


default_map_environ = {
    # Map timeline objects into the oops context as 'timeline'
    'timeline.timeline': 'timeline',
    }


def make_app(app, config, template=default_error_template,
        content_type='text/html', error_render=None, oops_on_status=None,
        map_environ=None, tracker=None):
    """Construct a middleware around app that will forward errors via config.

    Any errors encountered by the app will be forwarded to config and an error
    page shown.

    If the body of a reply has already started the error will be forwarded to
    config and also re-raised.

    If there are no publishers, or an error is filtered, the error will be
    re-raised rather than an error page shown. This permits containing
    middleware to show custom errors (for 404's, for instance), perhaps even
    for just some occurences of the issue.

    :param app: A WSGI app.
    :param config: An oops.Config.
    :param template: Optional string template to use when reporting the oops to
        the client. If not supplied a default template is used (unless an
        error_render function has been supplied).
    :param content_type: The content type for error pages. Defaults to
        text/html.
    :param error_render: Optional custom renderer for presenting error reports
        to clients. Should be a callable taking the report as its only
        parameter.
    :param oops_on_status: Optional list of HTTP status codes that should
        generate OOPSes. OOPSes triggered by sniffing these codes will not
        interfere with the response being sent. For instance, if you do
        not expect any 404's from your application, you might set
        oops_on_status=['404'].
    :param map_environ: A dictionary of environment keys to look for, and if
        present map into the OOPS context when generating an OOPS. The value of
        the key determines the name given in the OOPS context. If None is passed
        the default_map_environ is used. Pass {} in to entirely disable mapping.
    :param tracker: A factory function to create a tracker. Trackers are used
        to allow variations on the WSGI environment to still use oops_wsgi. 
        See generator_tracker for the reference tracker used in regular WSGI
        environments. generator_tracker is used by default or when
        tracker=None.
    :return: A WSGI app.
    """
    def oops_middleware(environ, start_response):
        """OOPS inserting middleware.

        This has the following WSGI properties:
        * start_response is buffered until either write() is called, or the
          wrapped app starts yielding content.
        * Exceptions that are ignored by the oops config get re-raised.
        * socket errors and GeneratorExit errors are passed through without
        * being forward to the oops system.
        """
        environ['oops.report'] = {}
        environ['oops.context'] = {}
        state = {}
        def make_context(exc_info=None):
            context = dict(url=construct_url(environ), wsgi_environ=environ)
            context.update(environ.get('oops.context', {}))
            mapper = map_environ
            if mapper is None:
                mapper = default_map_environ
            for environ_key, context_key in mapper.items():
                if environ_key in environ:
                    context[context_key] = environ[environ_key]
            if exc_info is not None:
                context['exc_info'] = exc_info
            return context
        def oops_write(bytes):
            write = state.get('write')
            if write is None:
                status, headers = state.pop('response')
                # Signal that we have called start_response
                state['write'] = start_response(status, headers)
                write = state['write']
            write(bytes)
        def oops_start_response(status, headers, exc_info=None):
            if exc_info is not None:
                # The app is explicitly signalling an error (rather than
                # returning a page describing the error). Capture that and then
                # forward to the containing element verbatim. In future we might
                # choose to add the OOPS id to the headers (but we can't fiddle
                # the body as it is being generated by the contained app.
                report = config.create(make_context(exc_info=exc_info))
                ids = config.publish(report)
                try:
                    if ids:
                        headers = list(headers)
                        headers.append(('X-Oops-Id', str(report['id'])))
                    state['write'] = start_response(status, headers, exc_info)
                    return state['write']
                finally:
                    del exc_info
            else:
                if oops_on_status:
                    for sniff_status in oops_on_status:
                        if status.startswith(sniff_status):
                            report = config.create(make_context())
                            report['HTTP_STATUS'] = status.split(' ')[0]
                            config.publish(report)
                state['response'] = (status, headers)
            return oops_write
        try:
            def ensure_start_response():
                if 'write' not in state:
                    status, headers = state.pop('response')
                    # Signal that we have called start_response
                    state['write'] = start_response(status, headers)
            def on_exception(exc_info):
                report = config.create(make_context(exc_info=exc_info))
                ids = config.publish(report)
                if not ids or 'write' in state:
                    # No OOPS generated, no oops publisher, or we have already
                    # transmitted the wrapped apps headers - either way we can't
                    # replace the content with a clean error, so let the wsgi
                    # server figure it out.
                    raise
                headers = [('Content-Type', content_type)]
                headers.append(('X-Oops-Id', str(report['id'])))
                start_response(
                    '500 Internal Server Error', headers, exc_info=exc_info)
                del exc_info
                if error_render is not None:
                    return error_render(report)
                else:
                    return template % report
            if tracker is None:
                tracker_factory = generator_tracker
            else:
                tracker_factory = tracker
            return tracker_factory(
                ensure_start_response, ensure_start_response, on_exception,
                app(environ, oops_start_response))
        except socket.error:
            raise
        except Exception:
            exc_info = sys.exc_info()
            return [on_exception(exc_info)]

    return oops_middleware


def generator_tracker(on_first_bytes, on_finish, on_error, app_body):
    """A wrapper for generators that calls the OOPS hooks as needed.

    :param on_first_bytes: Called as on_first_bytes() when the first bytes from
        the app body are available but before they are yielded.
    :param on_finish: Called as on_finish() when the app body is fully
        consumed.
    :param on_error: Called as on_error(sys.exc_info()) if a handleable error
        has occured while consuming the generator. Errors like GeneratorExit
        are not handleable.
    :param app_body: The iterable body for the WSGI app. This may be a simple
        list or a generator - it is merely known to meet the iterator protocol.
    """
    try:
        called_first = False
        for bytes in app_body:
            if not called_first:
                called_first = True
                on_first_bytes()
            yield bytes
        on_finish()
    except socket.error:
        # start_response, which iteration can trigger a call into, may raise
        # socket.error when writing if the client has disconnected: thats not
        # an OOPS condition. This does potentially mask socket.error issues in
        # the appserver code, so we may want to change this to callback to
        # determine if start_response has been called upstream, and if so, to
        # still generate an OOPS.
        raise
    except GeneratorExit:
        # Python 2.4
        raise
    except Exception:
        exc_info = sys.exc_info()
        yield on_error(exc_info)
