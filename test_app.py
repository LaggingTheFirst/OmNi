import requests
import os

BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin"

def test_flow():
    session = requests.Session()
    
    # 1. Login
    print("Testing Login...")
    login_data = {'username': USERNAME, 'password': PASSWORD}
    r = session.post(f"{BASE_URL}/auth/login", data=login_data)
    if r.url == f"{BASE_URL}/dashboard":
        print("Login Successful!")
    else:
        print(f"Login Failed. redirected to {r.url}")
        return

    # 2. Upload
    print("Testing Upload...")
    with open("requirements.txt", "rb") as f:
        files = {'files[]': ('test_requirements.txt', f, 'text/plain')}
        r = session.post(f"{BASE_URL}/upload", files=files)
    
    if r.status_code == 200:
        print("Upload request completed.")
    else:
        print(f"Upload failed: {r.status_code}")

    # 3. Check Dashboard for file
    print("Verifying file on Dashboard...")
    r = session.get(f"{BASE_URL}/dashboard")
    if "test_requirements.txt" in r.text:
        print("File found in dashboard!")
    else:
        print("File NOT found in dashboard.")
        # print(r.text)

    # Note: Extracting ID to delete/download would require parsing HTML, 
    # skipping for this quick check unless necessary.

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test crashed: {e}")
