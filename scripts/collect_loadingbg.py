from pathlib import Path
import shutil

SRC = Path("ClientAssets/JP/AssetBundles/loadingbg")
DST = Path("current_loadingbg")

DST.mkdir(parents=True, exist_ok=True)

for f in SRC.glob("*"):
    if f.is_file():
        shutil.copy2(f, DST / f.name)
