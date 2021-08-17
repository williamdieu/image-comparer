# image-comparer

## About

image-comparer compares all images capable of being read by OpenCV in the directory it is placed in, including all subfolders. I designed it for personal purposes to remove all my duplicate images I had on my storage devices. It is capable of auto deleting based off date created, but there also exists a step-by-step review process in case you wish to keep images in certain folders.

## Changes

- Use template matching to determine whether image is a subset of another image, and so provide option of removing sub image.
- Use resizing to determine whether an image is another image but resized (as if image super resolution was used).
- Develop C++ alternative if there is a performance increase.
- Develop an executable file.
