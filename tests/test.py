import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def print_response(r):
    print("Status:", r.status_code)
    try:
        print("Response:", json.dumps(r.json(), indent=2))
    except:
        print("Response:", r.text)
    print()

print("=== Test #1: Set Help Text ===")
r = requests.post(f"{BASE_URL}/help-text", json={"help_text": "Welcome to the help popup!"})
print_response(r)

print("=== Test #2: Set Help Title ===")
r = requests.post(f"{BASE_URL}/help-title", json={"title": "Help Window Title"})
print_response(r)

print("=== Test #3: Open Help Window ===")
r = requests.post(f"{BASE_URL}/open-help-window")
print_response(r)

sleep(5)

print("=== Test #4: Close Help Window ===")
r = requests.post(f"{BASE_URL}/close-help-window")
print_response(r)

print("=== Test #5: Close Help Window Again ===")
r = requests.post(f"{BASE_URL}/close-help-window")
print_response(r)
