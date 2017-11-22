.PHONY: index check

index:
	./makeindex.py

check:
	./check_wheels.py ${PWD}

git_squash:
	GIT_EDITOR="sed -i -e 's;\[deploy\].*;squash\!\ squashed\ wheels;g' -e 's;pick;reword;g'" \
		git rebase -i --root \
	&& GIT_EDITOR=true git rebase -i --autosquash --root
