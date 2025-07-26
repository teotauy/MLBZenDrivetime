#!/usr/bin/env python3
"""
Backend API Test for MLB Drive Time Application
Tests the /api/calculate endpoint to verify Google Maps integration
"""

import requests
import json
import sys
import time

# Test configuration
BASE_URL = "http://localhost:8001"
API_ENDPOINT = f"{BASE_URL}/api/calculate"

def test_api_calculate_endpoint():
    """Test the /api/calculate endpoint with sample data"""
    print("=" * 60)
    print("TESTING MLB DRIVE TIME BACKEND API")
    print("=" * 60)
    
    # Test data from the review request
    test_data = {
        "startLocation": "79045",  # ZIP code from user's example
        "destinations": ["401 E Jefferson St, Phoenix, AZ 85004"]  # Chase Field (Arizona Diamondbacks)
    }
    
    print(f"Testing endpoint: {API_ENDPOINT}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    print("-" * 60)
    
    try:
        # Make POST request to the API
        response = requests.post(
            API_ENDPOINT,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response Data: {json.dumps(result, indent=2)}")
                
                # Validate response structure
                if isinstance(result, list) and len(result) > 0:
                    first_result = result[0]
                    required_fields = ['address', 'driveDurationMinutes', 'driveDistanceMiles']
                    
                    print("\n" + "=" * 40)
                    print("RESPONSE VALIDATION")
                    print("=" * 40)
                    
                    all_fields_present = True
                    for field in required_fields:
                        if field in first_result:
                            value = first_result[field]
                            print(f"✅ {field}: {value} ({type(value).__name__})")
                        else:
                            print(f"❌ Missing field: {field}")
                            all_fields_present = False
                    
                    if all_fields_present:
                        # Check if we got valid drive time data
                        drive_time = first_result.get('driveDurationMinutes')
                        drive_distance = first_result.get('driveDistanceMiles')
                        
                        if drive_time is not None and drive_distance is not None:
                            print(f"\n✅ SUCCESS: API returned valid drive time data")
                            print(f"   Drive Time: {drive_time:.1f} minutes")
                            print(f"   Drive Distance: {drive_distance:.1f} miles")
                            return True
                        else:
                            print(f"\n❌ FAILURE: API returned null values for drive time/distance")
                            print("   This might indicate Google Maps API issues")
                            return False
                    else:
                        print(f"\n❌ FAILURE: Response missing required fields")
                        return False
                else:
                    print(f"\n❌ FAILURE: Invalid response format - expected array with results")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ FAILURE: Invalid JSON response - {e}")
                print(f"Raw response: {response.text}")
                return False
                
        else:
            print(f"❌ FAILURE: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ FAILURE: Connection error - Backend service not accessible at {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ FAILURE: Request timeout - API took longer than 30 seconds")
        return False
    except Exception as e:
        print(f"❌ FAILURE: Unexpected error - {e}")
        return False

def test_api_error_handling():
    """Test API error handling with invalid input"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    # Test with missing startLocation
    test_cases = [
        {
            "name": "Missing startLocation",
            "data": {"destinations": ["401 E Jefferson St, Phoenix, AZ 85004"]},
            "expected_status": 400
        },
        {
            "name": "Missing destinations",
            "data": {"startLocation": "79045"},
            "expected_status": 400
        },
        {
            "name": "Empty destinations array",
            "data": {"startLocation": "79045", "destinations": []},
            "expected_status": 400
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                API_ENDPOINT,
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == test_case['expected_status']:
                print(f"✅ PASS: Got expected status {response.status_code}")
            else:
                print(f"❌ FAIL: Expected status {test_case['expected_status']}, got {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL: Error during test - {e}")
            all_passed = False
    
    return all_passed

def check_service_status():
    """Check if the backend service is running"""
    print("=" * 60)
    print("CHECKING SERVICE STATUS")
    print("=" * 60)
    
    try:
        # Simple health check - try to connect to the base URL
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Backend service is accessible at {BASE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend service not accessible at {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error checking service status: {e}")
        return False

def main():
    """Main test execution"""
    print("Starting MLB Drive Time Backend API Tests...")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check service status first
    if not check_service_status():
        print("\n❌ CRITICAL: Backend service is not running!")
        print("Please check supervisor status: sudo supervisorctl status")
        sys.exit(1)
    
    # Run main API test
    api_test_passed = test_api_calculate_endpoint()
    
    # Run error handling tests
    error_test_passed = test_api_error_handling()
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if api_test_passed:
        print("✅ Main API functionality: WORKING")
    else:
        print("❌ Main API functionality: FAILED")
    
    if error_test_passed:
        print("✅ Error handling: WORKING")
    else:
        print("❌ Error handling: FAILED")
    
    overall_success = api_test_passed and error_test_passed
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED - Backend API is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 SOME TESTS FAILED - Backend API has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()