from pathlib import Path
import shutil

src = Path("ClientAssets/JP/AssetBundles/loadingbg")
dst = Path("current_loadingbg")

dst.mkdir(parents=True, exist_ok=True)

if not src.exists():
    print("Source directory does not exist:", src)
    exit(0)

for f in src.iterdir():
    if f.is_file():
        shutil.copy2(f, dst / f.name)
