import os
import ssl
import urllib.request

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Create cache directory if it doesn't exist
os.makedirs('build/web-cache', exist_ok=True)

# Download required files
files = {
    'default.tmpl': '489f66f53e526d7110d2d34527229eca.tmpl',
    'favicon.png': '38e02d124325c756243ee99a92e528ed.png'
}

for file, cache_name in files.items():
    url = f'https://pygame-web.github.io/archives/0.9/{file}'
    cache_path = f'build/web-cache/{cache_name}'
    if not os.path.exists(cache_path):
        print(f'Downloading {url}...')
        urllib.request.urlretrieve(url, cache_path)

# Now run pygbag
os.system('python3 -m pygbag --build .')
