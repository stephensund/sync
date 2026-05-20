from pathlib import Path
import shutil
import os

src = Path("ClientExtract/JP/gallerypic")
dst = Path("current_gallerypic")

dst.mkdir(parents=True, exist_ok=True)

if not src.exists():
    print("Source directory does not exist:", src)
    # Debug: show what's available
    for parent in ["ClientExtract/JP", "ClientAssets/JP", "ClientExtract", "ClientAssets"]:
        if os.path.exists(parent):
            print(f"  {parent}/:", os.listdir(parent))
    exit(0)

# Clear dst first
for f in dst.iterdir():
    f.unlink()

count = 0
for f in src.iterdir():
    if f.is_file():
        shutil.copy2(f, dst / f.name)
        count += 1

print(f"Collected {count} files from {src}")
