import os
import urllib.request

os.makedirs('sounds', exist_ok=True)
urls = {
    'move.mp3': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/sound/standard/Move.mp3',
    'capture.mp3': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/sound/standard/Capture.mp3',
    'check.mp3': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/sound/standard/Check.mp3',
    'mate.mp3': 'https://raw.githubusercontent.com/lichess-org/lila/master/public/sound/standard/Victory.mp3'
}

for name, url in urls.items():
    path = f"sounds/{name}"
    try:
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print(f"Error downloading {name}: {e}")
print("Audio download script complete.")
