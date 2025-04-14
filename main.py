#-*- coding:utf-8 -*-

import pytesseract
import PIL
import os
import pathlib
import re
import easyocr
from doctr.io import DocumentFile
from doctr.models import ocr_predictor


def dor():
  """
  better solution
  """
  model = ocr_predictor(det_arch="db_resnet50", reco_arch="crnn_vgg16_bn", pretrained=True)
  files = os.listdir("./media/")
  code = []
  for pathFile in files:
    if pathFile.endswith(".png") or pathFile.endswith(".jpg") or pathFile.endswith(".jpeg"):
      img = DocumentFile.from_images(f"./media/{pathFile}")
      text = model(img)
      result = text.export()
      lockPrint = True
      _tmp = []
      for item in result["pages"][0]["blocks"]:
        for item1 in item["lines"]:
          for item2 in item1["words"]:
            if lockPrint == False and len(item2["value"])>2:
              _tmp.append(re.search("[a-zA-Z]+", item2["value"]).group(0))
            if item2["value"].isnumeric() and len(item2["value"])>4:
              lockPrint = False
      code.append(" ".join(_tmp))
  print(code)


def eocr():
  """
  faster answer
  """
  files = os.listdir("./media/")
  reader = easyocr.Reader(["en"])
  for pathFile in files:
    if pathFile.endswith(".png") or pathFile.endswith(".jpg") or pathFile.endswith(".jpeg"):
      text = reader.readtext(f"./media/{pathFile}")
      lockPrint = True
      for item in text:
        if lockPrint == False:
          print(item[1])
        if item[1].isnumeric():
          lockPrint = False
      print("-----------")
      

def pts():
  """
  average result
  """
  result = []
  files = os.listdir("./media/")
  for pathFile in files:
    if pathFile.endswith(".png") or pathFile.endswith(".jpg") or pathFile.endswith(".jpeg"):
      text = pytesseract.image_to_string(f"./media/{pathFile}", lang="eng")
      code = re.search(' [A-Za-z]{3} [A-Za-z]{3} [A-Za-z]{3} ', text)
      print(code)
      print("---------------------")



if __name__ == "__main__":
  dor()