
# opensale ecommerce for raspberry pi
## beta now available!

### Installation for Raspberry Pi
Stay up to date!
```
$ sudo apt-get update
```
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
### Git opensale
```
$ cd Documents/
$ mkdir Copies/
$ cd Copies/
$ mkdir opensale/
$ cd opensale/
$ git clone https://github.com/Kenstogram/opensale.git
```
Install the required dependencies for developing this project:
```
$ sudo apt-get install build-essential python3-dev python3-pip python3-cffi 
$ sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
$ sudo apt-get install libjpeg8-dev
$ python3 -m pip install pillow psycopg2-binary
$ python3 -m pip install -r requirements_dev.txt
```
### Configure psql for raspberry pi
```
$ sudo apt install postgresql libpq-dev postgresql-client
$ sudo apt install postgresql-client-common -y
$ sudo su postgres
```
### Follow configuration steps (Note: do not use these passwords and names for production)
```
$ createuser postgres -P --interactive
```
### Update Settings.py (Note: do not use these passwords and names for production)
```
#settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'myPassword',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
### Exit psql after prompt 
```
$exit
```
### Prepare database
```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```
### Migrate Waitingblock for Waitinglist App (optional)
```
$ python3 manage.py migrate waitingblock
```
### Install Node for Ubuntu
https://github.com/nodesource/distributions/blob/master/README.md
```
$ curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
$ sudo apt-get install -y nodejs
$ node -v
```
### Configure NPM for raspberry pi
```
$ npm install --save-dev webpack-cli
$ npm i -D extract-text-webpack-plugin@next
```
### Install front-end
```
$ npm install
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
