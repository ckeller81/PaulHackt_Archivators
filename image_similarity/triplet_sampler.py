import numpy as np
import os
import re


def list_pictures(directory, ext="jpg"):
    return [os.path.join(root, f)
            for root, _, files in os.walk(directory) for f in files
            if re.match(r'([\w]+\.(?:' + ext + '))', f)]

def get_positive_images(image_name, image_names, num_pos_images=1):
    random_numbers = np.arange(len(image_names))
    np.random.shuffle(random_numbers)
    if int(num_pos_images) > (len(image_names) - 1):
        num_pos_images = len(image_names) - 1

    pos_count = 0
    positive_images = []

    for random_number in list(random_numbers):
        if image_names[random_number] != image_name:
            positive_images.append(image_names[random_number])
            pos_count += 1
            if int(pos_count) > (int(num_pos_images) - 1):
                break

    return positive_images

def get_negative_images(all_images, image_names, num_neg_images=1):
    random_numbers = np.arange(len(all_images))
    np.random.shuffle(random_numbers)
    if int(num_neg_images) > (len(all_images) - 1):
        num_neg_images = len(all_images) - 1

    neg_count = 0
    negative_images = []

    for random_number in list(random_numbers):
        if all_images[random_number] not in image_names:
            negative_images.append(all_images[random_number])
            neg_count += 1
            if neg_count > (int(num_neg_images) - 1):
                break

    return negative_images

if __name__ == '__main__':
    data_path = "./data"
    classes = [d for d in os.listdir(data_path)]
    classes.remove("val")

    all_images = list()

    for class_ in classes:
        all_images += (list_pictures(os.path.join(data_path, class_)))

    i = 1
    triplets = list()
    for class_ in classes:
        image_names = list_pictures(os.path.join(data_path, class_))
        for image_name in image_names:
            query_image = image_name
            positive_images = get_positive_images(image_name, image_names)[0]
            negative_images = get_negative_images(all_images, set(image_names))[0]

            triplets.append(f"{query_image},")
            triplets.append(f"{positive_images},")
            triplets.append(f"{negative_images}\n")

    with open("./triplets.txt", "w") as f:
        f.write("".join(triplets))