"""
Build script with a runtime error.
"""
from navio.builder import task


@task()
def images():
    """Prepare images. Raises IOError."""
    global ran_images
    ran_images = True
    raise OSError


@task(images)
def android():
    """Package Android app."""
    global ran_android
    print("android")
    ran_android = True
