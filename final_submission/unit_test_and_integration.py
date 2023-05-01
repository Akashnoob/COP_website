from app import app,db,User
from flask import url_for
from flask_login import current_user
import unittest
from werkzeug.security import generate_password_hash, check_password_hash
from flask.testing import FlaskClient
from io import BytesIO

class FlaskTest(unittest.TestCase):
    def test_login(self):
        tester = app.test_client(self)
        response = tester.get("/")
        statuscode = response.status_code
        self.assertAlmostEqual(statuscode,200)
    def test_login_success(self):
        tester = app.test_client(self)
        response = tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():  # create an application context
            user = User.query.filter_by(email='u1@gmail.com').first()
            self.assertEqual(response.request.path, '/home/{}'.format(user.id))
    def test_login_failure(self):
        tester = app.test_client(self)
        response = tester.post('/', data=dict(email='test@example.com', password='wrong_password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid credentials', response.data)
    def test_signup(self):
        tester = app.test_client(self)
        response = tester.get("/signup")
        statuscode = response.status_code
        self.assertAlmostEqual(statuscode,200)
    def test_signup_success(self):
        tester = app.test_client(self)
        response = tester.post('/signup', data=dict(email='test2@example.com', username='testuser2', password='password', cfpassword='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app.app_context():  # create an application context
            user = User.query.filter_by(email='test2@example.com').first()
            self.assertEqual(response.request.path, '/home/{}'.format(user.id))
            self.assertIsNotNone(user)
            User.query.filter_by(email='test2@example.com').delete()
            db.session.commit()
    def test_signup_failure(self):
        # Test with invalid data
        tester = app.test_client(self)
        response = tester.post('/signup', data=dict(email='test', username='t', password='pwd', cfpassword='pwd'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email', response.data)
        self.assertEqual(response.request.path, '/signup')
        response = tester.post('/signup', data=dict(email='test@gmail.com', username='t', password='pwd', cfpassword='pwd'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User name must be greater than 1 character', response.data)
        self.assertEqual(response.request.path, '/signup')
        response = tester.post('/signup', data=dict(email='test@gmail.com', username='testuser', password='pwd', cfpassword='pwd'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password must be at least 7 characters', response.data)
        self.assertEqual(response.request.path, '/signup')
        response = tester.post('/signup', data=dict(email='u1@gmail.com', username='testuser1', password='password', cfpassword='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already exists', response.data)
        self.assertEqual(response.request.path, '/signup')
        response = tester.post('/signup', data=dict(email='user1@gmail.com', username='user1', password='password', cfpassword='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists', response.data)
        self.assertEqual(response.request.path, '/signup')
    def test_logout(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        response = tester.get("/logout")
        statuscode = response.status_code
        self.assertAlmostEqual(statuscode,302)
    def products(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        response = tester.get('/products')
        self.assertEqual(response.status_code, 200)
    def cart(self):
        tester = app.test_client(self)
        response = tester.get('/cart')
        self.assertEqual(response.status_code, 401)
    def profile(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        response = tester.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user1', response.data)     
    def test_view_unautorised(self):
        tester = app.test_client(self)
        response = tester.get('/profile')
        self.assertEqual(response.status_code, 401)
    def test_profile_update(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        response = tester.post('/profile',data= {'form_type': 'profile_update', 'username': 'user1', 'email': 'u1@gmail.com','password':'user123','bio':'artist','profession':'photography'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)
    def test_profile_photo_update(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        with open('test.jpg', 'rb') as f:
            response = tester.post('/profile/1', data={'form_type':'photo_update','profile_pic': (BytesIO(f.read()), 'test.jpg')})
        self.assertEqual(response.status_code, 200) 
        self.assertIn(b'Profile picture updated successfully', response.data)
        with app.app_context():
            updated_user = User.query.filter_by(id=1).first()
            self.assertNotEqual(updated_user.profile_pic, 'public/unknown.jpg')
    def test_profile_pic_delete(self):
        tester = app.test_client(self)
        tester.post('/', data=dict(email='u1@gmail.com', password='user123'), follow_redirects=True)
        response = tester.post('/profile/1', data=dict(form_type='photo_update', delete_profile_pic='yes'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile picture deleted successfully', response.data)
        with app.app_context():
            updated_user = User.query.filter_by(id=1).first()
            self.assertEqual(updated_user.profile_pic, 'public/unknown.png')


if __name__ == "__main__" :
    unittest.main()
    