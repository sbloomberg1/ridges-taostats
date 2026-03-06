import urllib.request
import json
import re

# Try wallet explorer page
url = "https://taostats.io/wallet/5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM"

try:
    print(f"Trying: {url}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read().decode()
        print(f"Status: {response.status}")
        # Look for API endpoints in the HTML
        api_patterns = re.findall(r'https?://[^\s\"<>\']+api[^\s\"<>\']*', content)
        print(f"Found API patterns: {list(set(api_patterns))[:20]}")
except Exception as e:
    print(f"Failed: {e}")
