import unittest
import json
from app import app
import database

class BuildMindAITests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_page_renders_concept2(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BuildMind', response.data)
        self.assertIn(b'Plan Smarter. Build Better.', response.data)
        self.assertIn(b'AI Construction Planning Agent', response.data)
        self.assertIn(b'Plan your projects with AI and build your dream.', response.data)
        self.assertIn(b'Welcome Back!', response.data)
        self.assertIn(b'Sign in to continue to BuildMind AI.', response.data)
        self.assertIn(b'Email Address', response.data)
        self.assertIn(b'Password', response.data)
        self.assertIn(b'Remember me', response.data)
        self.assertIn(b'Forgot password?', response.data)
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'Continue with Google', response.data)
        self.assertIn(b'Register', response.data)

    def test_unauthenticated_redirect_to_login(self):
        # Without session, accessing dashboard should redirect to login
        response = self.app.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_login_authentication_success_and_logout(self):
        # 1. Login with demo user
        res = self.app.post('/login', data={
            'email': 'rajesh.sharma@buildmind.ai',
            'password': 'password123',
            'remember': 'on'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard Concept 1', res.data)
        self.assertIn(b'Rajesh Sharma', res.data)

        # 2. Access AI planner while authenticated
        planner_res = self.app.get('/planner')
        self.assertEqual(planner_res.status_code, 200)
        self.assertIn(b'AI Construction Planner', planner_res.data)

        # 3. Logout
        logout_res = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(logout_res.status_code, 200)
        self.assertIn(b'Welcome Back!', logout_res.data)

    def test_login_authentication_failure(self):
        res = self.app.post('/login', data={
            'email': 'rajesh.sharma@buildmind.ai',
            'password': 'wrongpassword'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid email address or password', res.data)

    def test_registration_and_login(self):
        import time
        new_email = f"test.engineer.{int(time.time() * 1000)}@buildmind.ai"
        reg_res = self.app.post('/register', data={
            'full_name': 'Test Engineer',
            'email': new_email,
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'role': 'Structural Auditor'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b'Dashboard Concept 1', reg_res.data)

    def test_forgot_password_reset(self):
        # Reset password for demo user
        res = self.app.post('/forgot-password', data={
            'email': 'rajesh.sharma@buildmind.ai',
            'new_password': 'updatedpassword123'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Password reset successfully', res.data)

        # Test login with newly updated password
        login_res = self.app.post('/login', data={
            'email': 'rajesh.sharma@buildmind.ai',
            'password': 'updatedpassword123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Dashboard Concept 1', login_res.data)

        # Restore default password for ongoing consistency
        database.reset_user_password('rajesh.sharma@buildmind.ai', 'password123')

    def test_generate_plan_flow(self):
        # Login first
        self.app.post('/login', data={
            'email': 'rajesh.sharma@buildmind.ai',
            'password': 'password123'
        })

        payload = {
            'project_name': 'Lotus Tower Residential',
            'construction_type': 'Residential',
            'location': 'Hyderabad, Telangana',
            'plot_area': 4000,
            'builtup_area': 5200,
            'floors': 'G + 2 Floors',
            'bedrooms': 4,
            'bathrooms': 4,
            'budget': 11000000,
            'start_date': '2026-06-01',
            'completion_date': '2027-05-31',
            'ai_options': [
                'Construction Planning', 'Material Requirements', 'Budget Estimation',
                'Labour Requirements', 'Construction Timeline', 'Risk Analysis', 'Resource Planning'
            ]
        }
        response = self.app.post('/api/generate-plan', json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['plan']['phases']), 9)
        self.assertEqual(len(data['plan']['materials']), 5)

if __name__ == '__main__':
    unittest.main()
