"""
Utility functions for the core app
"""
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def compress_image(image_file, max_size=(1920, 1080), quality=85):
    """
    Compress and resize an uploaded image
    
    Args:
        image_file: Uploaded image file
        max_size: Maximum dimensions (width, height)
        quality: JPEG quality (1-100)
    
    Returns:
        Compressed image file
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if larger than max_size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create new InMemoryUploadedFile
        compressed_file = InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_file.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        
        return compressed_file
        
    except Exception as e:
        # If compression fails, return original file
        print(f"Image compression failed: {e}")
        return image_file


def optimize_profile_photo(photo_file):
    """
    Optimize profile photos
    - Max size: 800x800
    - Quality: 85%
    """
    return compress_image(photo_file, max_size=(800, 800), quality=85)


def optimize_company_logo(logo_file):
    """
    Optimize company logos
    - Max size: 600x600
    - Quality: 90%
    """
    return compress_image(logo_file, max_size=(600, 600), quality=90)


def optimize_blog_image(image_file):
    """
    Optimize blog featured images
    - Max size: 1920x1080
    - Quality: 85%
    """
    return compress_image(image_file, max_size=(1920, 1080), quality=85)

