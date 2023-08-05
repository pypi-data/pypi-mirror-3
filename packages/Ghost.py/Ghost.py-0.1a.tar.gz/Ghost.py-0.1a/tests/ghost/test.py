# -*- coding: utf-8 -*-
import threading
from unittest import TestCase
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from ghost import Ghost


class ServerThread(threading.Thread):
    """Starts a Tornado HTTPServer from given WSGI application.

    :param app: The WSGI application to run.
    :param port: The port to run on.
    """
    def __init__(self, app, port=5000):
        self.app = app
        self.port = port
        super(ServerThread, self).__init__()

    def run(self):
        self.http_server = HTTPServer(WSGIContainer(self.app))
        self.http_server.listen(self.port)
        self.io = IOLoop.instance()
        self.io.start()

    def join(self, timeout=None):
        if hasattr(self, 'http_server'):
            self.http_server.stop()
            del self.http_server


class GhostTestCase(TestCase):
    """TestCase that provides a ghost instance and manage
    an HTTPServer running a WSGI application.
    """
    port = 5000
    display = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'ghost'):
            cls.ghost = Ghost(display=cls.display)
        return super(GhostTestCase, cls).__new__(cls, *args, **kwargs)

    def __call__(self, result=None):
        """Does the required setup, doing it here
        means you don't have to call super.setUp
        in subclasses.
        """
        self._pre_setup()
        super(GhostTestCase, self).__call__(result)
        self._post_teardown()

    def create_app(self):
        """Returns your WSGI application for testing.
        """
        raise NotImplementedError

    def _post_teardown(self):
        """Stops HTTPServer instance."""
        self.server_thread.join()
        self.ghost.delete_cookies()
        if self.display:
            self.ghost.hide()

    def _pre_setup(self):
        """Starts HTTPServer instance from WSGI application.
        """
        self.server_thread = ServerThread(self.create_app(), self.port)
        self.server_thread.daemon = True
        self.server_thread.start()
        if self.display:
            self.ghost.show()
