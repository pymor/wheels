.PHONY: index check

index:
	./makeindex.py

check:
	./check_wheels.py ${PWD}

git_squash:
	GIT_EDITOR="sed -i -e 's;\[deploy\].*;squash\!\ squashed\ wheels;g' -e 's;pick;reword;g'" \
		git rebase -i --root -X theirs \
	&& GIT_EDITOR=true git rebase -i --autosquash --root -X theirs

cleanup: git_squash prune index

prune:
	./prune_branches.py
