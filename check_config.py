import sys
sys.path.insert(0, r'C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages')
from importlib.resources import as_file, files
import pathlib

p = pathlib.Path(r'C:\Users\Administrator\AppData\Local\Programs\Python\Python311\Lib\site-packages\azlassets\config\user_config_template.yml')
if p.exists():
    print("FILE EXISTS:")
    print(p.read_text(encoding='utf-8'))
else:
    print("FILE NOT FOUND")
    # Try package resources
    try:
        with as_file(files("azlassets").joinpath("config/user_config_template.yml")) as fp:
            print("Via package resources:", fp)
            print(fp.read_text())
    except Exception as e:
        print("Error:", e)
