import urllib
from PIL import Image


def download_thumbnail(url, name):
    image_path = "public_queue/static/images/thumbnails/{}.jpg".format(name)
    urllib.request.urlretrieve(url, image_path)
    # crop 1/8 from end and start
    image_object = Image.open(image_path)
    width, height = image_object.size
    crop_coords = (0, height // 8, width, height - height // 8)
    cropped_image = image_object.crop(crop_coords)
    cropped_image.save(image_path)
