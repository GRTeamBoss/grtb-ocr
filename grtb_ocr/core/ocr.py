#-*- coding:utf-8 -*-

import re
from PIL import Image
from doctr.models import ocr_predictor
import numpy
import math
import io

class OCR:

  __MODEL = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True, detect_orientation=True, detect_language=True, assume_straight_pages=False, preserve_aspect_ratio=True)
  __BLOCKWORDS = ("SMS", "PIN")


  def __init__(self, blob: bytes) -> None:
    self.blob = blob

  def detect(self) -> str:
    crop, angle = self.imageCrop(Image.open(io.BytesIO(self.blob)).convert("RGB"))
    img = Image.open(io.BytesIO(self.blob)).convert("RGB").rotate(angle).crop(crop)
    __tmp = []
    text = self.__MODEL([numpy.asarray(img)]).export()
    for item in text["pages"][0]["blocks"]:
      for item1 in item["lines"]:
        for item2 in item1["words"]:
          if len(item2["value"]) == 3 and item2["value"] not in self.__BLOCKWORDS:
            var = re.search("[A-Z]{3}", item2["value"])
            if var == None:
              pass
            else:
              __tmp.append(var.group(0))
    if __tmp:
      return " ".join(__tmp)
    else:
      return "Nothing detected! Try again!"

  def imageCrop(self, img: Image) -> tuple[tuple[int, int, int, int], float]:
    w, h = img.size
    angle = 0.0
    text = self.__MODEL([numpy.asarray(img)])
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

    return (preWidth, preHeight, endWidth, endHeight), angle