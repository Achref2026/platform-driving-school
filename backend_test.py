import requests
import sys
import json
from datetime import datetime

class DrivingSchoolAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_data = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if headers.get('Content-Type') == 'application/json':
                    response = requests.post(url, json=data, headers=headers)
                else:
                    response = requests.post(url, data=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    print(f"Error detail: {error_detail}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_get_states(self):
        """Test getting Algerian states"""
        success, response = self.run_test(
            "Get States",
            "GET",
            "api/states",
            200
        )
        if success and 'states' in response:
            print(f"Found {len(response['states'])} states")
            if len(response['states']) == 58:
                print("✅ Correct number of states (58)")
            else:
                print(f"⚠️ Expected 58 states, got {len(response['states'])}")
        return success

    def test_register_user(self):
        """Test user registration"""
        # Generate a unique email
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        email = f"test_user_{timestamp}@example.com"
        
        data = {
            "email": email,
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+213555123456",
            "address": "123 Test Street",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "state": "Alger"
        }
        
        success, response = self.run_test(
            "Register User",
            "POST",
            "api/auth/register",
            200,
            data=data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"✅ User registered successfully with ID: {self.user_data.get('id')}")
            print(f"✅ Token received: {self.token[:10]}...")
        
        return success

    def test_login(self, email="test@example.com", password="Test123!"):
        """Test login with existing credentials"""
        data = {
            "email": email,
            "password": password
        }
        
        success, response = self.run_test(
            "Login",
            "POST",
            "api/auth/login",
            200,
            data=data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            print(f"✅ Login successful for user: {self.user_data.get('email')}")
            print(f"✅ User role: {self.user_data.get('role')}")
        
        return success

    def test_get_driving_schools(self):
        """Test getting driving schools"""
        success, response = self.run_test(
            "Get Driving Schools",
            "GET",
            "api/driving-schools",
            200
        )
        
        if success and 'schools' in response:
            print(f"Found {len(response['schools'])} driving schools")
        
        return success

    def test_dashboard(self):
        """Test getting dashboard data"""
        if not self.token:
            print("❌ Cannot test dashboard without authentication")
            return False
            
        success, response = self.run_test(
            "Get Dashboard",
            "GET",
            "api/dashboard",
            200
        )
        
        if success:
            print("✅ Dashboard data retrieved successfully")
            if 'user' in response:
                print(f"✅ Dashboard contains user data")
            if 'enrollments' in response:
                print(f"✅ Dashboard contains {len(response['enrollments'])} enrollments")
            if 'documents' in response:
                print(f"✅ Dashboard contains {len(response['documents'])} documents")
            if 'notifications' in response:
                print(f"✅ Dashboard contains {len(response['notifications'])} notifications")
        
        return success

def main():
    # Get backend URL from environment or use default
    backend_url = "http://localhost:8001"
    
    print(f"🚀 Testing Driving School Platform API at {backend_url}")
    tester = DrivingSchoolAPITester(backend_url)
    
    # Run tests
    tests = [
        tester.test_health_check,
        tester.test_get_states,
        tester.test_register_user,
        tester.test_get_driving_schools,
        tester.test_dashboard
    ]
    
    for test_func in tests:
        test_func()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())