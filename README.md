# Running

```zsh
python3 -m venv .env
. ./.env/bin/activate
pip install poetry
poetry install
export TELEGRAM_TOKEN=[YOUR_TOKEN]
export WEBHOOK_SECRET=[YOUR_SECRET]
export BASE_WEBHOOK_URL=[URL] # Example: https://example.com
export WEBHOOK_SSL_CERT=[PATH] # Example: /path/to/cert.pem
export WEBHOOK_SSL_PRIV=[PATH] # Example: /path/to/private.key
poetry run python grtb_ocr
```


```zsh
make install
export TELEGRAM_TOKEN=[YOUR_TOKEN]
export WEBHOOK_SECRET=[YOUR_SECRET]
export BASE_WEBHOOK_URL=[URL] # Example: https://example.com
export WEBHOOK_SSL_CERT=[PATH] # Example: /path/to/cert.pem
export WEBHOOK_SSL_PRIV=[PATH] # Example: /path/to/private.key
make run
# <make help> for some issues
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
