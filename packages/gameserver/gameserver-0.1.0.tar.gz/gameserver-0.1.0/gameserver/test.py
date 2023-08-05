import unittest
import webapp2

# from the app main.py
import main

class TestHandlers(unittest.TestCase):
   def test_hello(self):
       # Build a request object passing the URI path to be tested.
       # You can also pass headers, query arguments etc.
       request = webapp2.Request.blank('/')
       # Get a response for that request.
       response = request.get_response(main.app)

       # Let's check if the response is correct.
       self.assertEqual(response.status_int, 200)
       self.assertEqual(response.body, 'Hello, world!')