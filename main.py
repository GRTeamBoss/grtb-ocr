#-*- coding:utf-8 -*-

import os
import re
from PIL import Image
from doctr.models import ocr_predictor
from string import ascii_uppercase
import numpy
import math


def dor():
  """
  better solution
  """
  PATH = "./media/"
  model = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True, detect_orientation=True, detect_language=True, assume_straight_pages=False, preserve_aspect_ratio=True)
  files = os.listdir(PATH)
  code = []
  blockWords = ("SMS", "PIN")
  for pathFile in files:
    if pathFile.endswith("07.04.jpg") or pathFile.endswith("07.04.jpeg"):
      imagePathFile = f"{PATH}{pathFile}"
      print(pathFile)
      # angle = ifRotated(Image.open(imagePathFile).convert("RGB"))
      crop, angle = imageCrop(Image.open(imagePathFile).convert("RGB"))
      print("angle: ", angle)
      print("crop: ", crop)
      pilimg = Image.open(imagePathFile).convert("RGB").rotate(angle).crop(crop)
      text = model([numpy.asarray(pilimg)])
      result = text.export()
      _tmp = []
      for item in result["pages"][0]["blocks"]:
        for item1 in item["lines"]:
          for item2 in item1["words"]:
            if len(item2["value"]) == 3 and item2["value"] not in blockWords:
              var = re.search("[A-Z]{3}", item2["value"])
              if var == None:
                pass
              else:
                print(var.group(0))
                _tmp.append(var.group(0))
      print("----------------")
      # text.show() # for debugging
      code.append(" ".join(_tmp))
  print(code)

def imageCrop(image):
  model = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True, detect_orientation=True, detect_language=True, assume_straight_pages=False, preserve_aspect_ratio=True)
  w, h = image.size
  angle = 0.0
  text = model([numpy.asarray(image)])
  for item in text.export()["pages"][0]["blocks"]:
    for item1 in item["lines"]:
      for item2 in item1["words"]:
        if item2["value"] == "HIMOYA":
          minimalX = min(item2["geometry"][0][0], item2["geometry"][2][0])
          maximalX = max(item2["geometry"][1][0], item2["geometry"][3][0])
          diffWidth = maximalX - minimalX
          preWidth = (minimalX - diffWidth) * w
          endWidth = (maximalX + diffWidth / 2) * w
          minimalY = min(item2["geometry"][0][1], item2["geometry"][1][1])
          maximalY = max(item2["geometry"][2][1], item2["geometry"][3][1])
          diffHeight = maximalY - minimalY
          preHeight = minimalY * h
          endHeight = (minimalY + (diffHeight * 8)) * h

          if item2["geometry"][0][1] != item2["geometry"][1][1]:
            k = 1
            b = item2["geometry"][1][1] - item2["geometry"][0][1]
            if b < 0:
              k = -1
            b = abs(b)
            a = item2["geometry"][1][0] - item2["geometry"][0][0]
            angle = k*math.degrees(math.atan(b/a))


  # text.show() # for debugging
  return (preWidth, preHeight, endWidth, endHeight), angle





def ifRotated(image):
  image, status = isRotatedToRight(image)
  if status == False:
    image, status = isRotatedToLeft(image)
  return image


def isRotatedToRight(image: Image):
  w, h = image.size
  k = 0
  j = 0
  arrayFromTopToBottom = []
  arrayFromTopToLeft = []
  for i in range(0, 100):
    arrayFromTopToBottom.append(image.getpixel((w-1, i)))
  for i in range(w-1, w-101, -1):
    arrayFromTopToLeft.append(image.getpixel((i, 0)))
  for item in arrayFromTopToBottom:
    if item == (255, 255, 255):
      k += 1
    else:
      break
  for item in arrayFromTopToLeft:
    if item == (255, 255, 255):
      j += 1
    else:
      break
  if j == 100 or k == 100:
    return 0.0, True
  if j > 0:
    print(j, k)
    angle = math.degrees(math.atan(k/j))
    return angle, True
  else:
    return image, False
  
def isRotatedToLeft(image: Image):
  w, h = image.size
  k = 0
  j = 0
  arrayFromTopToBottom = []
  arrayFromTopToRight = []
  for i in range(0, 100):
    arrayFromTopToBottom.append(image.getpixel((0, i)))
  for i in range(0, 100):
    arrayFromTopToRight.append(image.getpixel((i, 0)))
  for item in arrayFromTopToBottom:
    if item == (255, 255, 255):
      k += 1
    else:
      break
  for item in arrayFromTopToRight:
    if item == (255, 255, 255):
      j += 1
    else:
      break
  if j == 100 or k == 100:
    return 0.0, False
  if j > 0:
    angle = -math.degrees(math.atan(k/j))
    return angle, True
  else:
    return 0.0, False



if __name__ == "__main__":
  dor()