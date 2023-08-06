import unittest

class TestIt(unittest.TestCase):
    def _getAUT(self):
        from bucho.wsgi import application
        return application

    def test_show(self):
        app = self._getAUT()
        response = {}
        def start_response(status, headers):
            response['status'] = status
            response['headers'] = headers
            
        environ = {'PATH_INFO': '/show'}
        info = app(environ, start_response)
        self.assertEqual(response['status'], '200 OK')

    def test_not_found(self):
        app = self._getAUT()
        response = {}
        def start_response(status, headers):
            response['status'] = status
            response['headers'] = headers
            
        environ = {'PATH_INFO': '/nothing'}
        info = app(environ, start_response)
        self.assertEqual(response['status'], '404 Not Found')
