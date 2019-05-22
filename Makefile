check: unittest functest

unittest:
	python -m unittest discover

functest:
	./functest.sh
