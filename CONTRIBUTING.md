### Formatting
We mostly follow pep8, but we allow up to 120 character lines.  Our CI checks formatting with yapf, so please ensure your pull requests match yapf's pep8 style or the build will fail.

### Formatting
Before you push, make sure your formatting matches pep8:
```
$ python -m yapf --in-place --recursive waitingblock
```
