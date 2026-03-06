import urllib.request
import json
import re

# Get the dash page and look for JS files
url = "https://dash.taostats.io"

try:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read().decode()
        
        # Find JS files
        js_files = re.findall(r'<script[^>]+src=["\']([^"\'>]+)["\'>]', content)
        print(f"JS files found: {js_files[:10]}")
        
        # Look for API base URLs
        api_bases = re.findall(r'(https?://[^"\'\s]+)/api', content)
        print(f"API base URLs: {list(set(api_bases))[:10]}")
        
        # Look for API endpoint definitions in inline scripts
        inline_api = re.findall(r'api["\'>\s*:\s*["\']([^"\'>]+)["\'>]', content)
        print(f"Inline API definitions: {list(set(inline_api))[:10]}")
        
except Exception as e:
    print(f"Failed: {e}")
