import unittest
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        result = self.app.get('/')
        self.assertEqual(result.data, b'Hello, World!')

    def test_non_existent_route(self):
        result = self.app.get('/nonexistent')
        self.assertEqual(result.status_code, 404)

    def test_hello_world_content_type(self):
        result = self.app.get('/')
        self.assertEqual(result.content_type, 'text/html; charset=utf-8')

    def test_hello_world_charset(self):
        result = self.app.get('/')
        self.assertTrue('charset=utf-8' in result.headers['Content-Type'])

if __name__ == '__main__':
    unittest.main()
