generate_test_data:
	pipenv run python generate_test_data.py

unit:
	pipenv run python -m unittest discover app

e2e:
	pipenv run python -m unittest discover e2e

coverage:
	./coverage

start:
	pipenv run python main.py

.PHONY: generate_test_data unit e2e coverage start
