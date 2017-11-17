.PHONY: index check

index:
	./makeindex.py

check:
	./check_wheels.py .
