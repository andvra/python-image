from os import listdir
from os.path import isfile, join
from random import randint


def get_input_image_path():
    allowed_file_types = ('.png', '.jpg')
    image_dir_path = 'images'
    all_images = [f for f in listdir(
        image_dir_path) if isfile(join(image_dir_path, f)) and f.endswith(allowed_file_types)]

    if len(all_images) == 0:
        print('No images available in directory ' +
              image_dir_path + '. Add an image')

    image_path = image_dir_path + '/' + \
        all_images[randint(0, len(all_images) - 1)]
    return image_path
