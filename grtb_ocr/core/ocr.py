#-*- coding:utf-8 -*-

import re
import math
import io

from PIL import Image
from doctr.models import ocr_predictor
import numpy

class OCR:

  """
  Args:
    blob (bytes): image raw content

  Returns:
    None
  """

  __MODEL = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True, detect_orientation=True, detect_language=True, assume_straight_pages=False, preserve_aspect_ratio=True)
  __BLOCKLETTERS = ("C", "H", "I", "J", "O", "Q", "U", "W", "V", "Y")
  __DETECTION = (r".IMOYA", r"H.MOYA", r"HI.OYA", r"HIM.YA", r"HIMO.A", r"HIMOY.", r"HIMO..", r".IMOY.", r"..MOYA", r"HIMO", r"IMOY", r"MOYA")


  def __init__(self, blob: bytes) -> None:
    self.blob = blob
    self.img = Image.open(io.BytesIO(self.blob))

  def detect(self) -> tuple[list[io.BytesIO], list[str]]:
    detectHimoyaAndRotatedAngle = self.findHimoya()
    if detectHimoyaAndRotatedAngle != 0.0:
      self.img = self.img.rotate(detectHimoyaAndRotatedAngle)
    detectThreeLetterWords = self.findWordsWithThreeLetters()
    if len(detectThreeLetterWords) == 0:
      return None, ["Nothing detected!"]
    detectCodeViaWords = self.findCodeViaDetectedWords(detectedWords=detectThreeLetterWords)
    if len(detectCodeViaWords) == 0:
      return None, ["Nothing detected!"]
    detectCropSection = self.findCropSectionViaCodeMeta(detectedCode=detectCodeViaWords)
    self.img = self.img.crop(detectCropSection)
    croppedImageIO = io.BytesIO()
    self.img.save(croppedImageIO, "JPEG")
    croppedImageIO.seek(0)
    pos = [[detectCodeViaWords[i][1][0][0], i] for i in range(len(detectCodeViaWords))]
    pos.sort()
    result = [detectCodeViaWords[item[1]][0] for item in pos]
    return croppedImageIO.read(), result


  def findHimoya(self, angle=0.0, eta=0, detectedWords=[], rotated=False, totalRotateAngle=0, detected=False):
    print("[totalRotateAngle] - ", totalRotateAngle)
    if totalRotateAngle == 360.0:
      return angle
    if angle != 0.0:
      print("[angle] [rotate] - ", angle)
      self.img = self.img.rotate(angle)
    w, h = self.img.size
    ocrDetection = self.__MODEL([numpy.asarray(self.img)])
    textExport = ocrDetection.export()
    rotateAngle = 0.0
    for textLine in textExport["pages"][0]["blocks"]:
      for textWords in textLine["lines"]:
        for textWord in textWords["words"]:
          print("[textWord['value']] - ", textWord["value"])
          isHimoya = [re.match(subj, textWord["value"]) for subj in self.__DETECTION]
          if isHimoya.count(None) != 12:
            detected = True
            topLeft, topRight, bottomRight, bottomLeft = textWord["geometry"]
            if topLeft[1] > bottomLeft[1] and topLeft[1] > bottomRight[1]:
              length = bottomLeft[0]*w - bottomRight[0]*w # 3x - 2x
              height = bottomLeft[1]*h - bottomRight[1]*h # 3y - 2y
              rotateAngle = math.degrees(math.atan(height/length))
              print("[rotateAngle] - ", rotateAngle)
              rotateAngle += float(180)
              print("[rotateAngle] [eta=0] - ", rotateAngle, (rotateAngle + totalRotateAngle))
              return rotateAngle
            else:
              if topRight[1] > bottomLeft[1]:
                length = topRight[0]*w - topLeft[0]*w # 1x - 0x
                height = topLeft[1]*h - topRight[1]*h # 0y - 1y
                rotateAngle = math.degrees(math.atan(height/length)) * -1
                print("[rotateAngle] [eta=0] - ", rotateAngle, (rotateAngle + totalRotateAngle))
                return rotateAngle
              else:
                if topLeft[1] > topRight[1] and topLeft[1] > bottomRight[1]:
                  length = topRight[0]*w - topLeft[0]*w # 1x - 0x
                  height = topLeft[1]*h - topRight[1]*h # 0y - 1y
                  rotateAngle = math.degrees(math.atan(height/length)) * -1
                  print("[rotateAngle] [eta=0] - ", rotateAngle, (rotateAngle + totalRotateAngle))
                  return rotateAngle
                else:
                  length = topRight[0]*w - topLeft[0]*w # 1x - 0x
                  height = topLeft[1]*h - topRight[1]*h # 0y - 1y
                  rotateAngle = math.degrees(math.atan(height/length)) * -1
                  print("[rotateAngle] [eta=0] - ", rotateAngle, (rotateAngle + totalRotateAngle))
                  return rotateAngle
    if detected == False:
      print("[detected] - ", detected)
      print("[!!!] Rotate to 30 degrees")
      return self.findHimoya(angle=float(30), totalRotateAngle=float(30)+totalRotateAngle)


  def findWordsWithThreeLetters(self, angle=0.0, eta=0, detectedWords=[], rotated=False, rotateCount=0, detected=False):
    print("[###] findWordsWithThreeLetters")
    ocrDetection = self.__MODEL([numpy.asarray(self.img)])
    textExport = ocrDetection.export()
    for textLine in textExport["pages"][0]["blocks"]:
      for textWords in textLine["lines"]:
        for textWord in textWords["words"]:
          isUpper = re.match(r"[ABDEFGKLMNPRSTXZ]{3}", textWord["value"])
          print("[textWord['value']] - ", textWord["value"])
          if len(textWord["value"]) == 3 and isUpper is not None:
            print("[textWord['value']] [confirmed] - ", textWord["value"])
            detectedWords.append([textWord["value"], textWord["geometry"]])
    return detectedWords

  def findCodeViaDetectedWords(self, angle=0.0, eta=0, detectedWords=[], rotated=False, rotateCount=0, detected=False):
    w, h = self.img.size
    averageHeightWords = []
    findedWordInSection = []
    findedWord = 0
    for item in detectedWords[-2:]:
      topLeft, topRight, bottomRight, bottomLeft = item[1]
      averageHeightWords.append(abs(bottomLeft[1]*h - topLeft[1]*h))
    heightStep = int(str(max(averageHeightWords))[0])
    print("[heightStep] - ", heightStep)
    for item in detectedWords:
      topLeft, topRight, bottomRight, bottomLeft = item[1]
      findedWordInSection.append(item)
      findedWord += 1
    print("[findedWord] - ", findedWord)
    print("[findedWordInSection] - ", findedWordInSection)
    if findedWord >= 2:
      j = 0
      for i in range(0, len(findedWordInSection)):
        i = i+j
        wordHeight = int(str(findedWordInSection[i][1][3][1]*h - findedWordInSection[i][1][0][1]*h)[0])
        print("[word] - ", findedWordInSection[i][0])
        print("[wordHeight] - ", wordHeight, findedWordInSection[i][1][3][1]*h - findedWordInSection[i][1][0][1]*h)
        if wordHeight < heightStep:
          j -= 1
          findedWord -= 1
          findedWordInSection.pop(i)
    if findedWord > 3:
      if findedWordInSection[-3][1][2][1] < findedWordInSection[-2][1][0][1]:
        print("[findedWord] [confirmed] - ", 2)
        print("[findedWordInSection] [confirmed] - ", findedWordInSection[-2:])
        return findedWordInSection[-2:]
      if findedWordInSection[-4][1][2][1] < findedWordInSection[-3][1][0][1]:
        print("[findedWord] [confirmed] - ", 3)
        print("[findedWordInSection] [confirmed] - ", findedWordInSection[-3:])
        return findedWordInSection[-3:]
    print("[findedWord] [confirmed] - ", findedWord)
    print("[findedWordInSection] [confirmed] - ", findedWordInSection)
    return findedWordInSection



  def findCropSectionViaCodeMeta(self, detectedCode=[]):
    w, h = self.img.size
    eta = 0
    topCrop = 0
    leftCrop = 0
    rightCrop = 0
    bottomCrop = 0
    for item in detectedCode:
      if eta == 0:
        topLeft, topRight, bottomRight, bottomLeft = item[1]
        topCrop = min(topLeft[1], topRight[1])
        leftCrop = min(topLeft[0], bottomLeft[0])
        rightCrop = max(topRight[0], bottomRight[0])
        bottomCrop = max(bottomLeft[1], bottomRight[1])
        eta += 1
      else:
        topLeft, topRight, bottomRight, bottomLeft = item[1]
        topCrop = min(topCrop, min(topLeft[1], topRight[1]))
        leftCrop = min(leftCrop, min(topLeft[0], bottomLeft[0]))
        rightCrop = max(rightCrop, max(topRight[0], bottomRight[0]))
        bottomCrop = max(bottomCrop, max(bottomLeft[1], bottomRight[1]))
    print("[cropSection] - ", (leftCrop*w, topCrop*h, rightCrop*w, bottomCrop*h))
    return (leftCrop*w, topCrop*h, rightCrop*w, bottomCrop*h)