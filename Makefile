.SILENT:

PYTHON= python3
MAIN= a_maze_ing.py
CONFIG= config.txt
MYPY_FLAGS= --warn-return-any --warn-unused-ignores \
			 --ignore-missing-imports \
			 --disallow-untyped-defs
FOLDERS= ./infrastructure ./mazegen $(MAIN)
			 

.PHONY: all run install debug lint lint-strict clean fclean help

all: install run

run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)
	
install: 
	uv sync

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	$(PYTHON) -m flake8 $(FOLDERS)
	$(PYTHON) -m mypy $(MYPY_FLAGS) $(FOLDERS)


lint-strict:
	$(PYTHON) -m flake8 $(FOLDERS)
	$(PYTHON) -m mypy $(MYPY_FLAGS) --strict $(FOLDERS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	
fclean:
	rm -rf .venv

build:
	rm -rf dist
	uv build

help:
	echo "make install: generates the virtual environment and installs the dependencies"
	echo "make debug: launches the Pdb debugging tool"
	echo "make lint: run flake8 and mypy"
	echo "make lint-strict: run flake8 and mypy more strictly"
	echo "make clean: delete the cache"
	echo "make fclean: delete the virtual environnement"