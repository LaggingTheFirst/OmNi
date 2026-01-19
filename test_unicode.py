import requests
import os
from datetime import datetime

BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin"

def test_unicode_upload():
    session = requests.Session()
    
    # 1. Login
    print("--- Phase 1: Login ---")
    login_data = {'username': USERNAME, 'password': PASSWORD}
    try:
        r = session.post(f"{BASE_URL}/auth/login", data=login_data)
        if r.url.endswith("/dashboard") or r.status_code == 200:
            print("[OK] Login Successful!")
        else:
            print(f"[FAIL] Login Failed. Redirected to {r.url}")
            return
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        print("Make sure the server is running at http://localhost:5000")
        return

    # 2. Upload with Unicode Name
    print("\n--- Phase 2: Unicode Upload ---")
    unicode_filename = "테스트_文件_Ω_β.txt"
    content = b"This is a test file for Unicode filename support."
    
    files = {'files[]': (unicode_filename, content, 'text/plain')}
    data = {'is_public': 'true'}
    
    r = session.post(f"{BASE_URL}/upload", files=files, data=data)
    
    if r.status_code == 200:
        print(f"[OK] Upload request for '{unicode_filename}' completed.")
    else:
        print(f"[FAIL] Upload failed with status {r.status_code}")
        return

    # 3. Verify in Dashboard
    print("\n--- Phase 3: Dashboard Verification ---")
    r = session.get(f"{BASE_URL}/dashboard")
    
    # We use the normalized version since secure_filename_unicode might change space/dashes
    # but the characters themselves should remain if they are \w
    if unicode_filename in r.text:
        print(f"[OK] Unicode filename '{unicode_filename}' found in dashboard!")
    elif "테스트_文件_Ω_β.txt" in r.text:
         print(f"[OK] Exact match found!")
    else:
        print("[FAIL] Unicode filename NOT found in dashboard.")
        # print(r.text) # Uncomment for debug

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_unicode_upload()
