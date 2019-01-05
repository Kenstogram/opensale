### Formatting
We mostly follow pep8, but we allow up to 120 character lines.  Our CI checks formatting with yapf, so please ensure your pull requests match yapf's pep8 style or the build will fail.

### Installation on Raspberry Pi

Ensure you have virtualenv installed and on your path

```
$ which virtualenv
```

should return anything other than `virtualenv not found`

Create a new virtual environment with your machine's python3 as the default python

```
$ virtualenv -p python3 myenv
```

Activate your virtual environment

```
$ source myenv/bin/activate
```

Install the required dependencies for developing this project:
```

```
$ sudo apt-get install build-essential python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
$ sudo apt-get install libjpeg8-dev
$ python3 -m pip install pillow pysycopg2
$ python3 -m pip install -r requirements_dev.txt
```
Before you push, make sure your formatting matches pep8:

```
$ python -m yapf --in-place --recursive waitingblock
```

### Testing
Build the database by running all available migrations:

```
$ python manage.py migrate
```

You can run a local server by running this command from the root of the repo
```
$ python manage.py runserver

```
### Configure psql for raspberry pi
```
$ sudo apt-get update

```
```
$sudo apt install postgresql libpq-dev postgresql-client 
postgresql-client-common -y
```

```
$ sudo su postgres
```
### Follow configuration steps and update settings.py psql info

```
$ createuser pi -P --interactive
```

### Prepare database
```
$ python3 manage.py migrate
```
### Install front-end
```
$ npm install
```

### Install front-end
### Install Node for Ubuntu
https://github.com/nodesource/distributions/blob/master/README.md

### Configure NPM for raspberry pi

```
$curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
$sudo apt-get install -y nodejs
node -v

npm install --save-dev webpack-cli

 npm run build-assets
```
```
$ npm run build-emails
```
### Start development server
```

$ python3 manage.py runserver
```
### Configure NPM for raspberry pi

```
$ npm i -D extract-text-webpack-plugin@next

```

### Production

If you'd like to use this in production, please make sure to set the `SECRET_KEY` environment variable, like so:

```
SECRET_KEY=<a_secret_key> python manage.py runserver
```

