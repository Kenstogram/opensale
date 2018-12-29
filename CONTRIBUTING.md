### Formatting
We mostly follow pep8, but we allow up to 120 character lines.  Our CI checks formatting with yapf, so please ensure your pull requests match yapf's pep8 style or the build will fail.

### Developing

Ensure you have virtualenv installed and on your path

```
which virtualenv
```

should return anything other than `virtualenv not found`

Create a new virtual environment with your machine's python3 as the default python

```
virtualenv -p python3 myenv
```

Activate your virtual environment

```
source myenv/bin/activate
```

Install the required dependencies for developing this project:

```
python -m pip install -r requirements-dev.txt
```

Before you push, make sure your formatting matches pep8:

```
python -m yapf --in-place --recursive waitingblock
```

### Testing
Build the database by running all available migrations:

```
python manage.py migrate
```

You can run a local server by running this command from the root of the repo
```
python manage.py runserver

```
### Configure psql
configure psql
```
