# Running

```bash
python3 -m venv .env
. ./.env/bin/activate
pip install poetry
poetry install
export TELEGRAM_TOKEN=[YOUR_TOKEN]
poetry run python grtb_ocr
```

## Installation

### docTR

```bash
pip install python-doctr
pip install "python-doctr[tf]" ; echo "for TensorFlow"
pip install "python-doctr[torch]" ; echo "for PyTorch"
```

## more

[Medium Post](https://medium.com/data-science/top-5-python-libraries-for-extracting-text-from-images-c29863b2f3d "Medium Post")
