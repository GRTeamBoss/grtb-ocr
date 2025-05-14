install: 
	python3 -m venv .env; . ./.env/bin/activate; python -m pip install poetry; poetry install
run: 
	poetry run python grtb_ocr
clean: 
	rm -rf `find . -name __pycache__`
remove: 
	rm -rf .env/
help: 
	echo "Commands:\nmake install - install env and libs\nmake run - run package\nmake clean - remove tmp folders\nmake remove - remove env and libs"
