.PHONY: index check

index:
	./makeindex.py

check:
	./.ci/check_wheels.py .
