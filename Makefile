# One-command helpers. On Windows run the commands from a shell with Python 3.12 on PATH
# (for example Git Bash), or copy the command lines.
PY ?= python

.PHONY: venv test pack-install lock-check clean

venv:            ## create .venv and install runtime + test dependencies
	$(PY) -m venv .venv
	.venv/Scripts/python -m pip install -r requirements-lock.txt || .venv/bin/python -m pip install -r requirements-lock.txt

test:            ## run the full test suite on synthetic data (no competition data needed)
	$(PY) -m pytest -q

pack-install:    ## print the one-line installer that copies src/risk_weave into a SAS Studio home folder
	$(PY) tools/pack_for_vfl.py --install

lock-check:      ## show installed versions of the pinned packages
	$(PY) -m pip freeze | grep -iE "^(numpy|pandas|scikit-learn|scipy|xgboost|pytest)=="

clean:
	rm -rf .pytest_cache src/risk_weave/__pycache__ tests/__pycache__
