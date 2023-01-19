import boto3
from PIL import Image
import os
import logging

# Set up logging
logging.basicConfig(filename='transparent_images.log', level=logging.WARNING)

def check_transparency(bucket, key):
    # Open image file from S3
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image = Image.open(response['Body'])
    except Exception as e:
        logging.warning(f'Error opening image {key}: {e}')
        return None
    
    # Check if image has transparent pixels
    try:
        if image.mode == "RGBA":
            # Get image data and check if any pixels have alpha value < 255
            data = list(image.getdata())
            if any(pixel[3] < 255 for pixel in data):
                return True
        return False
    except Exception as e:
        logging.warning(f'Error checking transparency for image {key}: {e}')
        return None

def copy_image(src_bucket, src_key, dst_bucket):
    # Copy image from src_bucket to dst_bucket
    s3 = boto3.client('s3')
    try:
        s3.copy_object(Bucket=dst_bucket, CopySource={'Bucket': src_bucket, 'Key': src_key}, Key=src_key)
    except Exception as e:
        logging.warning(f'Error copying image {src_key} from {src_bucket} to {dst_bucket}: {e}')

def list_and_copy_images(src_bucket, dst_bucket):
    # List all image files in S3 bucket
    s3 = boto3.client('s3')
    try:
        objects = s3.list_objects(Bucket=src_bucket)['Contents']
    except Exception as e:
        logging.warning(f'Error listing objects in bucket {src_bucket}: {e}')
        return
    
    # Iterate through image files and check for transparency
    for obj in objects:
        key = obj['Key']
        if not key.endswith('.jpg') and not key.endswith('.png') and not key.endswith('.jpeg'):
            continue
        transparency = check_transparency(src_bucket, key)
        if transparency is None:
            continue
        if not transparency:
            copy_image(src_bucket, key, dst_bucket)
        else:
            logging.warning(f'Image {key} in {src_bucket} has transparent pixels')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", '--src_bucket', help='Name of the source bucket')
    parser.add_argument("-d", '--dst_bucket', help='Name of the destination bucket')
    args = parser.parse_args()
    list_and_copy_images(args.src_bucket, args.dst_bucket)