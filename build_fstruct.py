import os
from PIL import Image
import subprocess

# -------------------------
# Config
# -------------------------
project_folder = os.path.abspath(".")
png_icons = ["fstruct.png", "fstruct_alt.png"]
ico_icons = ["fstruct.ico", "fstruct_alt.ico"]
exe_names = ["FStruct", "FStruct_Alt"]
script_name = "fstruct.py"
config_file = "config.json"

# -------------------------
# Step 1: Convert PNG → ICO
# -------------------------
for png, ico in zip(png_icons, ico_icons):
    png_path = os.path.join(project_folder, png)
    ico_path = os.path.join(project_folder, ico)
    img = Image.open(png_path)
    img.save(ico_path, sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
    print(f"{ico} created successfully!")

# -------------------------
# Step 2: Build EXEs
# -------------------------
for exe_name, ico in zip(exe_names, ico_icons):
    print(f"Building {exe_name}.exe ...")
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--name={exe_name}",
        f"--icon={ico}",
        "--add-data", f"{config_file};.",
        script_name
    ]
    subprocess.run(cmd)
    print(f"{exe_name}.exe build completed!")

print("✅ All builds finished! Check the dist/ folder.")
