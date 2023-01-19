import os
import cv2
import argparse

# IO Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Input image path")
parser.add_argument("-o", "--output", help="Output directory to save")
args = parser.parse_args()

imageName = args.input
outputPath = args.output

# Cascade loader
faceCascade = cv2.CascadeClassifier()
faceCascade.load("haarcascade_frontalface_default.xml")

# Image reading
image = cv2.imread(imageName)

# Error handling for unidentified files
if image is None:
    print("Unidentified file with extension %s" % imageName.split(".")[-1])
    exit()

# Converting image to gray (necessary for haar cascade)
grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
grayImage = cv2.equalizeHist(grayImage)

# Check output path for saving without any problem
if not os.path.exists(outputPath):
    os.makedirs(outputPath)

# Detect faces
faces = faceCascade.detectMultiScale(grayImage)

# Cropping and saving faces that detected on input image
for c, faceBox in enumerate(faces):
    x1, y1, x2, y2 = faceBox[0], faceBox[1], faceBox[0] + faceBox[2], faceBox[1] + faceBox[3]
    croppedFace = image[y1:y2, x1:x2]
    cv2.imwrite(os.path.join(outputPath, "face_%s.jpg" % c), croppedFace)