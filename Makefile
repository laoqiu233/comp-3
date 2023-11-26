CODE = comp3

format: 
	poetry run python -m isort $(CODE)
	poetry run python -m black $(CODE)