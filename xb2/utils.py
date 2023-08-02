from loguru import logger
import hashlib
import os
from datetime import datetime, timedelta
from werkzeug.datastructures import  FileStorage
from PIL import Image, ExifTags
from xb2.models import File
import time
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.opt(depth=1).info(f"{func.__name__} done, cost {end_time - start_time:.2f} s")
        return result
    return wrapper


@profile
def save_file(file: FileStorage, save_dir: str) -> File:
    with Image.open(file) as img:
        img_bytes = img.tobytes()
        md5 = hashlib.md5(img_bytes).hexdigest()

        filepath = os.path.join(save_dir, md5)

        img = Image.open(file)
        img_size = len(img_bytes)
        img_exif = img.getexif()
        metadata = {}
        if img_exif is not None:
            for key, val in img_exif.items():
                if key in ExifTags.TAGS and isinstance(val, (str, int, float)):
                    metadata[ExifTags.TAGS[key]] = val


        width, height = img.size

        img.save(filepath, format="PNG")

        resize_dir = os.path.join(save_dir, "resize")
        os.makedirs(resize_dir, exist_ok=True)

        if width > 1280:
            width_percent = 1280 / float(img.width)
            
            new_height = int((float(img.height) * float(width_percent)))
            large_img_path = os.path.join(resize_dir, f"{md5}-large")
            img.resize((1280, new_height)).save(large_img_path, format="PNG")

        if width > 640:
            width_percent = 640 / float(img.width)
            
            new_height = int((float(img.height) * float(width_percent)))
            large_img_path = os.path.join(resize_dir, f"{md5}-medium")
            img.resize((640, new_height)).save(large_img_path, format="PNG")

        if width > 320:
            width_percent = 320 / float(img.width)
            
            new_height = int((float(img.height) * float(width_percent)))
            large_img_path = os.path.join(resize_dir, f"{md5}-thumbnail")
            img.resize((320, new_height)).save(large_img_path, format="PNG")

        return  File(
            originalname = file.filename,
            mimetype = file.mimetype,
            filename = md5,
            size = img_size,
            width = width,
            height = height,
            metadata_ = metadata
        )