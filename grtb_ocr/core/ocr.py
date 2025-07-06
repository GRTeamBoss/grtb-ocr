#-*- coding:utf-8 -*-

import re
from PIL import Image
from doctr.models import ocr_predictor
import numpy
import statistics
import math
import io

class OCR:

  """
  Args:
    blob (bytes): image raw content

  Returns:
    None
  """

  __MODEL = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True, detect_orientation=True, detect_language=True, assume_straight_pages=False, preserve_aspect_ratio=True)
  __BLOCKWORDS = ("SMS", "PIN", "EMS")
  __BLOCKLETTERS = ("C", "H", "I", "J", "O", "Q", "U", "W", "V", "Y")
  __DETECTION = (r".IMOYA", r"H.MOYA", r"HI.OYA", r"HIM.YA", r"HIMO.A", r"HIMOY.")


  def __init__(self, blob: bytes) -> None:
    self.blob = blob
    self.img = Image.open(io.BytesIO(self.blob))

  def detect(self) -> tuple[list[io.BytesIO], list[str]]:
    crops = self.imageCrop()
    result = []
    imagesIO = []
    detectedCode = []
    for imgCrop in crops:
      detectedCode = []
      crop, angle, detectedCode = imgCrop

      print("[crop] - ", crop)
      print("[angle] - ", angle)

      if detectedCode == False:
        result.append("Nothing detected!")
        break

      img = self.img.convert("RGB").rotate(angle).crop(crop)
      croppedImageIO = io.BytesIO()
      img.save(croppedImageIO, "JPEG")
      croppedImageIO.seek(0)

      imagesIO.append(croppedImageIO.read())
      result.append(" ".join(detectedCode))

    if detectedCode == False:
      return None, result

    return imagesIO, result

  def imageCrop(self) -> list[tuple[tuple[int, int, int, int], float]]:
    images = []
    detectedWords = []
    leftX = 0
    rightX = 0
    topY = 0
    bottomY = 0
    img, angle, _, words = self.findCodeInImage(0.0)
    if words == False:
      images.append(((False), False, False))
      print("[words] - ", words)
      return images
    w, h = img.size
    eta = 0
    upsideDown = False

    print("[words] - ", words)
    for item in words: detectedWords.append([min(item[1][0][1], item[1][1][1]), item[0]])

    firstCode = []
    secondCode = []
    thirdCode = []
    realFirstCode = 0
    realSecondCode = 0
    codeResult = []

    __tmp = []
    for i in range(len(detectedWords)): 
      __tmp.append([])
      for j in range(len(words)): __tmp[i].append([detectedWords[i][0] - min(words[j][1][0][1], words[j][1][1][1]), words[j][0]])
    __tmp.sort()
    __tmpSorted = []
    print("[__tmp] - ", __tmp)
    for item in __tmp:
      item.sort()
      if abs(item[1][0] - item[0][0]) >= 0.1: __tmpSorted.append([item[1][1], item[2][1]])
      else:
        if abs(item[2][0] - item[1][0]) >= 0.1: __tmpSorted.append([item[0][1], item[1][1]])
        else: __tmpSorted.append([item[0][1], item[1][1], item[2][1]])

    print("[__tmpSorted] - ", __tmpSorted)

    _tmp = []
    __buffer = 0
    __buffer1 = 0
    itemCheck1 = False
    itemCheck2 = False
    itemCheck3 = False
    for item in detectedWords:
      for item1 in words:
        if item[1] == item1[0]:
          if len(_tmp) == 0 and itemCheck1 == False:
            _tmp.append(item[1])
            __buffer = min(item1[1][0][0], item1[1][3][0])
            itemCheck1 == True
          elif len(_tmp) == 1 and itemCheck2 == False:
            if __buffer > min(item1[1][0][0], item1[1][3][0]): _tmp.insert(0, item[1])
            else: _tmp.append(item[1])
            __buffer1 = min(item1[1][0][0], item1[1][3][0])
            itemCheck2 == True
          else:
            if itemCheck3 == False:
              if __buffer > min(item1[1][0][0], item1[1][3][0]):
                if __buffer1 > min(item1[1][0][0], item1[1][3][0]): _tmp.insert(0, item[1])
                else: _tmp.insert(1, item[1])
              else: _tmp.append(item[1])
              itemCheck3 == True
            else: break
    print("[_tmp] - ", _tmp)
    if len(__tmpSorted[0]) == 2:
      firstCode, secondCode = [_tmp.index(__tmpSorted[0][0]), _tmp.index(__tmpSorted[0][1])]
      realFirstCode, realSecondCode = [min(firstCode, secondCode), max(firstCode, secondCode)]
      codeResult = [_tmp[realFirstCode], _tmp[realSecondCode]]
    elif len(__tmpSorted[0]) == 3:
      realThirdCode = 0
      firstCode, secondCode, thirdCode = [_tmp.index(__tmpSorted[0][0]), _tmp.index(__tmpSorted[0][1]), _tmp.index(__tmpSorted[0][2])]
      realFirstCode, realSecondCode, realThirdCode = [min(firstCode, secondCode, thirdCode), statistics.median([firstCode, secondCode, thirdCode]), max(firstCode, secondCode, thirdCode)]
      codeResult = [_tmp[realFirstCode], _tmp[realSecondCode], _tmp[realThirdCode]]
    else:
      pass
    
    print("[realFirstCode] - ", realFirstCode)
    print("[realSecondCode] - ", realSecondCode)
    print("[realThirdCode] - ", realThirdCode)

    for item in words:
      if item[0] in codeResult:
        if eta == 0:
          leftX, rightX, topY, bottomY = [min(item[1][0][0], item[1][3][0]), max(item[1][1][0], item[1][2][0]), min(item[1][0][1], item[1][1][1]), max(item[1][2][1], item[1][3][1])]
          if topY > bottomY:
            topY, bottomY, leftX, rightX = [min(item[1][2][1], item[1][3][1]), max(item[1][0][1], item[1][1][1]), min(item[1][1][0], item[1][2][0]), max(item[1][0][0], item[1][3][0])]
            upsideDown = True
          eta += 1
        else:
          if upsideDown == True:
            if leftX > min(item[1][1][0], item[1][2][0]): leftX = min(item[1][1][0], item[1][2][0])
            if rightX < max(item[1][0][0], item[1][3][0]): rightX = max(item[1][0][0], item[1][3][0])
            if topY > min(item[1][2][1], item[1][3][1]): topY = min(item[1][2][1], item[1][3][1])
            if bottomY < max(item[1][0][1], item[1][1][1]): bottomY = max(item[1][0][1], item[1][1][1])
          else:
            if leftX > min(item[1][0][0], item[1][3][0]): leftX = min(item[1][0][0], item[1][3][0])
            if rightX < max(item[1][1][0], item[1][2][0]): rightX = max(item[1][1][0], item[1][2][0])
            if topY > min(item[1][0][1], item[1][1][1]): topY = min(item[1][0][1], item[1][1][1])
            if bottomY < max(item[1][2][1], item[1][3][1]): bottomY = max(item[1][2][1], item[1][3][1])
    
    leftX *= w
    rightX *= w
    topY *= h
    bottomY *= h

    print("[codeResult] - ", codeResult)


    if upsideDown == True:
      print("[upsideDown] - ", upsideDown)
      print((w-rightX, h-bottomY, w-leftX, h-topY))
      codeResult.reverse()
      images.append(((w-rightX, h-bottomY, w-leftX, h-topY), angle+180, codeResult))
    else:
      print((leftX, topY, rightX, bottomY))
      images.append(((leftX, topY, rightX, bottomY), angle, codeResult))
    return images
  

  def findCodeInImage(self, angle: float, eta=0, words=[], rotated=False, totalRotate=0) -> tuple[Image.Image, float, int]:
    print("[eta] - ", eta)
    print("[angle] - ", angle)
    if eta >= 6:
        return False, False, False, False
    img = self.img.rotate(angle=float(angle+totalRotate))
    isUpper = False
    textDetected = self.__MODEL([numpy.asarray(img)])
    wordsInPicture = []
    word = 0
    rotate = False
    detected = False
    if rotated == False:
      for item in textDetected.export()["pages"][0]["blocks"]:
        for item1 in item["lines"]:
          for item2 in item1["words"]:
            isHimoya = [re.match(subj, item2["value"]) for subj in self.__DETECTION]
            print("[isHimoya] - ", isHimoya)
            if isHimoya.count(None) != 6:
              detected = True
              print("[detected] - ", detected)
              topLeft, topRight, bottomRight, bottomLeft = item2["geometry"]
              if topLeft[0] < bottomLeft[0]:
                if topLeft[1] > topRight[1]:
                  if bottomRight[1] < bottomLeft[1]:
                    x = topRight[0] - topLeft[0]
                    y = topLeft[1] - topRight[1]
                    rotateAngle = math.degrees(math.atan(y/x))*-1
                    rotate = True
              else:
                if topLeft[1] < topRight[1]:
                  if bottomRight[1] > bottomLeft[1]:
                    x = topRight[0] - topLeft[0]
                    y = topRight[1] - topLeft[1]
                    rotateAngle = math.degrees(math.atan(y/x))
                    rotate = True
              print("[rotate] - ", rotate)
              print("[rotated] - ", rotated)
              if rotate == True:
                print("[launch rotated function]")
                return self.findCodeInImage(rotateAngle, eta=eta+1, rotated=True, totalRotate=totalRotate+rotateAngle)
    else:
      detected = True
    if detected == False:
      print("[detected] - ", detected)
      print("[launch undetected function]")
      return self.findCodeInImage(angle+90, eta=eta+1, rotated=rotated, totalRotate=totalRotate+angle+90)
    else:
      for item in textDetected.export()["pages"][0]["blocks"]:
        for item1 in item["lines"]:
          for item2 in item1["words"]:
            print("[item2['value']] - ", item2["value"])
            isUpper = re.match(r"[ABDEFGKLMNPRSTXZ]{3}", item2["value"])
            if len(item2["value"]) == 3 and isUpper is not None:
              wordsInPicture.append([item2["value"], item2["geometry"]])
        print("[wordsInPicture] [final] - ", wordsInPicture)
        return img, angle+totalRotate, eta, wordsInPicture