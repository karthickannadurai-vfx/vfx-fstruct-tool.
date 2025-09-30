from PIL import Image
import os

png_files = ["fstruct.png", "fstruct_alt.png"]
ico_files = ["fstruct.ico", "fstruct_alt.ico"]

for png, ico in zip(png_files, ico_files):
    if not os.path.exists(png):
        print(f"ERROR: {png} not found in the folder!")
        continue
    img = Image.open(png)
    img.save(ico, sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
    print(f"{ico} created successfully!")
