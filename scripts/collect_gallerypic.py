from pathlib import Path
import shutil
import os

# gallerypic files are downloaded to ClientAssets/JP/AssetBundles/gallerypic/
# (they are part of the PIC version type)
src = Path("ClientAssets/JP/AssetBundles/gallerypic")
dst = Path("current_gallerypic")

dst.mkdir(parents=True, exist_ok=True)

if not src.exists():
    print(f"Source directory does not exist: {src}")
    # Debug: show what's actually in AssetBundles
    ab = Path("ClientAssets/JP/AssetBundles")
    if ab.exists():
        entries = list(ab.iterdir())
        print(f"  AssetBundles/ has {len(entries)} entries, showing first 20:")
        for e in sorted(entries)[:20]:
            print(f"    {e.name} ({'dir' if e.is_dir() else 'file'})")
    else:
        print("  AssetBundles/ dir NOT found")
        jp = Path("ClientAssets/JP")
        if jp.exists():
            print(f"  ClientAssets/JP/ contents: {[f.name for f in jp.iterdir()]}")
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
