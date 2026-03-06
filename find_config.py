import urllib.request
import re

# Get the dash page and look for config objects
url = "https://dash.taostats.io"

try:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read().decode()
        
        # Look for config objects
        config_patterns = re.findall(r"window\.__[^\s=]+=[^\;]+", content)
        print(f"Config patterns: {config_patterns[:5]}")
        
        # Look for API_URL or similar
        api_url_patterns = re.findall(r"[A-Z_]*API[A-Z_]*=[\'\"]([^\'\"]+)[\'\"]", content)
        print(f"API URL patterns: {api_url_patterns[:10]}")
        
        # Look for NEXT_PUBLIC or similar
        next_public = re.findall(r"NEXT_PUBLIC_[^\s=]+=[\'\"]?([^\'\"\s;]+)", content)
        print(f"NEXT_PUBLIC vars: {next_public[:10]}")
        
        # Look for any inline script with config
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
        for script in scripts[:3]:
            if "api" in script.lower() or "config" in script.lower():
                print(f"Script snippet: {script[:500]}")
                break
                
except Exception as e:
    print(f"Failed: {e}")
