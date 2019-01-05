# opensale ecommerce for raspberry pi
## beta now available!

### Installation for Raspberry Pi
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
$ sudo apt-get install build-essential python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
$ sudo apt-get install libjpeg8-dev
$ python3 -m pip install pillow pysycopg2
$ python3 -m pip install -r requirements_dev.txt
```
### GIT Waitingblock
```
$ cd Documents/
$ mkdir Copies/
$ cd Copies/
$ git clone https://github.com/Kenstogram/opensale.git
```
### Configure psql for raspberry pi
```
$ sudo apt-get update
$sudo apt install postgresql libpq-dev postgresql-client 
postgresql-client-common -y
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
### Migrate Waitingblock for Waitinglist App
```
$ python3 manage.py migrate Waitingblock
```
### Install front-end
```
$ npm install
```
### Install Node for Ubuntu
https://github.com/nodesource/distributions/blob/master/README.md
### Configure NPM for raspberry pi
```
$ curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
$ sudo apt-get install -y nodejs
$ node -v
$ npm install --save-dev webpack-cli
```
### Configure NPM for raspberry pi
```
$ npm i -D extract-text-webpack-plugin@next
$ npm run build-assets
$ npm run build-emails
```
### Start development server
```
$ python3 manage.py runserver
```
### Production
If you'd like to use this in production, please make sure to set the `SECRET_KEY` environment variable, like so:
```
SECRET_KEY=<a_secret_key> python manage.py runserver
```
