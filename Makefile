dependencies:
	virtualenv -p python3 venv
	venv/bin/pip install -r requirements.pip

clean:
	rm -rf venv/ *.egg-info/ dist/
	find . -name '*.pyc' | xargs rm -f

pretty: pep8 pylint

pep8:
	venv/bin/pep8 --ignore=E266 ka_infection tests

pylint:
	venv/bin/pylint --disable=W0142 --reports=no ka_infection

test: unit-test integration-test

unit-test:
	venv/bin/nosetests tests/unit --nocapture

integration-test:
	venv/bin/nosetests tests/integration --nocapture

.PHONY: clean test dependencies unit-test integration-test pep8 pylint pretty
