from PIL import Image

img = Image.open("fstruct.png")
img.save("fstruct.ico", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
