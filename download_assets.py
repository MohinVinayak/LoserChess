import os
import urllib.request

pieces = ['wk', 'wq', 'wr', 'wb', 'wn', 'wp', 'bk', 'bq', 'br', 'bb', 'bn', 'bp']

os.makedirs('assets', exist_ok=True)

for name in pieces:
    # We will map standard names to the ones our game expects
    # 'wK' -> 'wk', so we save them as 'wK.png' etc to match
    save_name = name[0] + name[1].upper()
    url = f"https://images.chesscomfiles.com/chess-themes/pieces/neo/150/{name}.png"
    filepath = f"assets/{save_name}.png"
    print(f"Downloading {save_name}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Failed to download {save_name}: {e}")

print("Done downloading assets.")
