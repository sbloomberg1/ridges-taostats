import urllib.request
import re

# Fetch and analyze JS files
base_url = "https://dash.taostats.io"
js_files = [
    "/_next/static/chunks/eba334d233d52591.js",
    "/_next/static/chunks/71098f8acdd7ed2d.js",
]

for js_file in js_files:
    try:
        url = base_url + js_file
        print(f"Fetching: {url}")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8", errors="ignore")
            
            # Look for API endpoints
            api_patterns = re.findall(r"/api/[^\s\"\'\)\,\+]+", content)
            unique_apis = list(set(api_patterns))
            print(f"API patterns: {[a for a in unique_apis if len(a) > 5][:20]}")
            
            # Look for fetch calls
            fetch_calls = re.findall(r'fetch\(["\']([^"\'\"]+)["\']\)', content)
            print(f"Fetch calls: {list(set(fetch_calls))[:10]}")
            
            break  # Just analyze first file
    except Exception as e:
        print(f"Failed: {e}")
