import glob
from PIL import Image

def resize_and_save(image_path: str):
    img = Image.open(image_path)
    img.thumbnail((256, img.size[1]))
    img.save(image_path, "JPEG")

if __name__ == '__main__':
    all_images = glob.glob("./data/*.jpg")
    for image_path in all_images:
        resize_and_save(image_path)