#-*- coding:utf-8 -*-

import re
from PIL import Image
from doctr.models import ocr_predictor
import numpy
import math
import statistics
from string import ascii_uppercase
import io

class OCR:

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

      img = self.img.convert("RGB").rotate(angle).crop(crop)
      croppedImageIO = io.BytesIO()
      img.save(croppedImageIO, "JPEG")
      croppedImageIO.seek(0)

      imagesIO.append(croppedImageIO.read())
      result.append(" ".join(detectedCode))

    return imagesIO, result

  def imageCrop(self) -> list[tuple[tuple[int, int, int, int], float]]:
    images = []
    detectedWords = []
    leftX = 0
    rightX = 0
    topY = 0
    bottomY = 0
    img, angle, _, words = self.findCodeInImage(0.0)
    w, h = img.size
    eta = 0
    upsideDown = False

    print("[words] - ", words)
    for item in words:
      detectedWords.append([min(item[1][0][1], item[1][1][1]), item[0]])

    firstCode = []
    secondCode = []
    thirdCode = []
    realFirstCode = 0
    realSecondCode = 0
    codeResult = []

    if len(detectedWords) < 4:
      __tmp = []
      __tmpSorted = []

      for item in words:
        __tmp.append(item[0])
      __tmpSorted.append(__tmp.copy())

      __tmp = []
      __buffer = 0
      __buffer1 = 0
      itemCheck1 = False
      itemCheck2 = False
      itemCheck3 = False
      for item in __tmpSorted[0]:
        for item1 in words:
          if item == item1[0]:
            if len(__tmp) == 0 and itemCheck1 == False:
              __tmp.append(item)
              __buffer = min(item1[1][0][0], item1[1][3][0])
              itemCheck1 == True
            elif len(__tmp) == 1 and itemCheck2 == False:
              if __buffer > min(item1[1][0][0], item1[1][3][0]):
                __tmp.insert(0, item)
              else:
                __tmp.append(item)
              __buffer1 = min(item1[1][0][0], item1[1][3][0])
              itemCheck2 == True
            else:
              if itemCheck3 == False:
                if __buffer > min(item1[1][0][0], item1[1][3][0]):
                  if __buffer1 > min(item1[1][0][0], item1[1][3][0]):
                    __tmp.insert(0, item)
                  else:
                    __tmp.insert(1, item)
                else:
                  __tmp.append(item)
                itemCheck3 == True
              else:
                break
      if len(detectedWords) == 2:
        firstCode = [__tmp.index(__tmpSorted[0][0]) for _ in __tmp]
        secondCode = [__tmp.index(__tmpSorted[0][1]) for _ in __tmp]
        firstCode = min(firstCode)
        secondCode = min(secondCode)
        realFirstCode = min(firstCode, secondCode)
        realSecondCode = max(firstCode, secondCode)
        codeResult = [None, None]
        codeResult[0] = __tmp[realFirstCode]
        codeResult[1] = __tmp[realSecondCode]
      elif len(detectedWords) == 3:
        realThirdCode = 0
        codeResult = [None, None, None]
        firstCode = [__tmp.index(__tmpSorted[0][0]) for _ in __tmp]
        secondCode = [__tmp.index(__tmpSorted[0][1]) for _ in __tmp]
        thirdCode = [__tmp.index(__tmpSorted[0][2]) for _ in __tmp]
        firstCode = min(firstCode)
        secondCode = min(secondCode)
        thirdCode = min(thirdCode)
        realFirstCode = min(firstCode, secondCode, thirdCode)
        realSecondCode = statistics.median([firstCode, secondCode, thirdCode])
        realThirdCode = max(firstCode, secondCode, thirdCode)
        codeResult[0] = __tmp[realFirstCode]
        codeResult[1] = __tmp[realSecondCode]
        codeResult[2] = __tmp[realThirdCode]
      else:
        pass
    else:
      __tmp = []
      __tmpSorted = []
      for i in range(len(detectedWords)):
        __tmp.append([])
        for j in range(len(words)):
          __tmp[i].append([detectedWords[i][0] - min(words[j][1][0][1], words[j][1][1][1]), words[j][0]])
      __tmp.sort()
      __tmpSorted = []
      __tmpSorted.append([])
      for item in __tmp:
        __tmpSorted[0].append([])

        if len(detectedWords) == 2:
          __tmpSorted.append([item[0][1], item[1][1]])
        elif len(detectedWords) >= 3:
          if abs(item[1][0] - item[0][0]) >= 0.1:
            __tmpSorted.append([item[1][1], item[2][1]])
          else:
            if abs(item[2][0] - item[1][0]) >= 0.04:
              __tmpSorted.append([item[0][1], item[1][1]])
            else:
              __tmpSorted.append([item[0][1], item[1][1], item[2][1]])

      __tmp = []
      __buffer = 0
      __buffer1 = 0
      itemCheck1 = False
      itemCheck2 = False
      itemCheck3 = False
      for item in detectedWords:
        for item1 in words:
          if item[1] == item1[0]:
            if len(__tmp) == 0 and itemCheck1 == False:
              __tmp.append(item)
              __buffer = min(item1[1][0][0], item1[1][3][0])
              itemCheck1 == True
            elif len(__tmp) == 1 and itemCheck2 == False:
              if __buffer > min(item1[1][0][0], item1[1][3][0]):
                __tmp.insert(0, item)
              else:
                __tmp.append(item)
              __buffer1 = min(item1[1][0][0], item1[1][3][0])
              itemCheck2 == True
            else:
              if itemCheck3 == False:
                if __buffer > min(item1[1][0][0], item1[1][3][0]):
                  if __buffer1 > min(item1[1][0][0], item1[1][3][0]):
                    __tmp.insert(0, item)
                  else:
                    __tmp.insert(1, item)
                else:
                  __tmp.append(item)
                itemCheck3 == True
              else:
                break
      if len(__tmpSorted[0]) == 2:
        firstCode = [__tmp.index(__tmpSorted[0][0]) for _ in __tmp]
        secondCode = [__tmp.index(__tmpSorted[0][1]) for _ in __tmp]
        firstCode = min(firstCode)
        secondCode = min(secondCode)
        realFirstCode = min(firstCode, secondCode)
        realSecondCode = max(firstCode, secondCode)
        codeResult = [None, None]
        codeResult[0] = __tmp[realFirstCode]
        codeResult[1] = __tmp[realSecondCode]
      elif len(__tmpSorted[0]) == 3:
        realThirdCode = 0
        codeResult = [None, None, None]
        firstCode = [__tmp.index(__tmpSorted[0][0]) for _ in __tmp]
        secondCode = [__tmp.index(__tmpSorted[0][1]) for _ in __tmp]
        thirdCode = [__tmp.index(__tmpSorted[0][2]) for _ in __tmp]
        firstCode = min(firstCode)
        secondCode = min(secondCode)
        thirdCode = min(thirdCode)
        realFirstCode = min(firstCode, secondCode, thirdCode)
        realSecondCode = statistics.median([firstCode, secondCode, thirdCode])
        realThirdCode = max(firstCode, secondCode, thirdCode)
        codeResult[0] = __tmp[realFirstCode]
        codeResult[1] = __tmp[realSecondCode]
        codeResult[2] = __tmp[realThirdCode]
      else:
        pass

    for item in words:
      if item[0] in codeResult:
        if eta == 0:
          leftX = min(item[1][0][0], item[1][3][0])
          rightX = max(item[1][1][0], item[1][2][0])
          topY = min(item[1][0][1], item[1][1][1])
          bottomY = max(item[1][2][1], item[1][3][1])
          if topY > bottomY:
            topY = min(item[1][2][1], item[1][3][1])
            bottomY = max(item[1][0][1], item[1][1][1])
            leftX = min(item[1][1][0], item[1][2][0])
            rightX = max(item[1][0][0], item[1][3][0])
            upsideDown = True
          eta += 1
        else:
          if upsideDown == True:
            if leftX > min(item[1][1][0], item[1][2][0]):
              leftX = min(item[1][1][0], item[1][2][0])
            if rightX < max(item[1][0][0], item[1][3][0]):
              rightX = max(item[1][0][0], item[1][3][0])
            if topY > min(item[1][2][1], item[1][3][1]):
              topY = min(item[1][2][1], item[1][3][1])
            if bottomY < max(item[1][0][1], item[1][1][1]):
              bottomY = max(item[1][0][1], item[1][1][1])
          else:
            if leftX > min(item[1][0][0], item[1][3][0]):
              leftX = min(item[1][0][0], item[1][3][0])
            if rightX < max(item[1][1][0], item[1][2][0]):
              rightX = max(item[1][1][0], item[1][2][0])
            if topY > min(item[1][0][1], item[1][1][1]):
              topY = min(item[1][0][1], item[1][1][1])
            if bottomY < max(item[1][2][1], item[1][3][1]):
              bottomY = max(item[1][2][1], item[1][3][1])
    
    leftX *= w
    rightX *= w
    topY *= h
    bottomY *= h

    __tmp = codeResult

    if upsideDown == True:
      print((w-rightX, h-bottomY, w-leftX, h-topY))
      __tmp.reverse()
      images.append(((w-rightX, h-bottomY, w-leftX, h-topY), angle+180, __tmp))
    else:
      print((leftX, topY, rightX, bottomY))
      images.append(((leftX, topY, rightX, bottomY), angle, __tmp))
    return images
  

  def findCodeInImage(self, angle: float, eta=0, words=[]) -> tuple[Image.Image, float, int]:
    img = self.img.rotate(angle=float(angle*eta))
    w, h = img.size
    isUpper = False
    textDetected = self.__MODEL([numpy.asarray(img)])
    wordsInPicture = []
    etaWords = []
    space = 0
    word = 0
    for item in textDetected.export()["pages"][0]["blocks"]:
      for item1 in item["lines"]:
        for item2 in item1["words"]:
          isUpper = re.match(r"[ABDEFGKLMNPRSTXZ]{3}", item2["value"])
          if len(item2["value"]) == 3 and isUpper is not None:
            wordsInPicture.append([item2["value"], item2["geometry"]])
            etaWords.append(item2["value"])
            word += 1
        print("[etaWords] - ", etaWords)
        if len(etaWords) == 0:
          word = 0
        if word == 3:
          print("[etaWords] [== 3] [final] - ", etaWords)
          return img, float(angle*eta), eta, wordsInPicture[-3::]
        if len(etaWords) < 2:
          etaWords = []
    if len(etaWords) >= 2:
      print("[etaWords] [>= 2] [final] - ", etaWords)
      if word == 2:
        return img, float(angle*eta), eta, wordsInPicture[-2::]
      return img, float(angle*eta), eta, wordsInPicture
    else:
      wordsInPicture = []
      newAngle = float(float(30) / (int(eta/12) + 1))
      k = int(eta/12) + 1
      img, angle, stack, words = self.findCodeInImage(newAngle, eta=eta+(1/k))
      return img, angle, stack, words