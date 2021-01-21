Setting up PowerMarket Dev Project
==================================

On MAC OSx
---


```bash
    # Needed packages
    brew update
    brew doctor
    brew install postgresql python3 node postgis
    
    # Install lunch to manage PostgreSQL
    gem install lunchy
    mkdir -p ~/Library/LaunchAgents
    cp /usr/local/Cellar/postgresql/9.6.3/homebrew.mxcl.postgresql.plist ~/Library/LaunchAgents/
    lunchy start postgres # instead of launchctl load -w ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist

    # Prepare the database with the Production dataset
    initdb /usr/local/var/postgres
    createuser --pwprompt tekramrewop
    createdb -Otekramrewop ebdb
    psql -d template1 -c "ALTER ROLE tekramrewop SUPERUSER;"
    psql -h localhost ebdb -U tekramrewop  < 2017-06-22_04-00.powermarketdb.sql

    # Create a Python3 virtual environment
    pip install virtualenv
    virtualenv -p python3 env
    source ./env/bin/activate

    # Install all the prerequesites Python and front packages
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    npm install

    # Prepare files to launch the webapp
    chmod u+x manage.py
    cp powermarket/settings/production.py powermarket/settings/local.py

    # Launch the website
    python3 manage.py makemigration
    python3 manage.py migrate # GEOSException, refer to errors bellow
    gulp
    python3 manage.py collectstatic --noinput
    python3 manage.py runserver
```

Errors
==================================

"GEOSException" when launching python manage.py migrate
---
```bash
  File "/Users/minux/Projects/PowerMarket/website/env/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py", line 191, in geos_version_info
    raise GEOSException('Could not parse version info string "%s"' % ver)
django.contrib.gis.geos.error.GEOSException: Could not parse version info string "3.6.2-CAPI-1.10.2 4d2925d6"
```
Look for the function: geos_version_info in env/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py

And change this line:
```bash
vi env/lib/python3.6/site-packages/django/contrib/gis/geos/libgeos.py
ver = geos_version().decode() 
#TO
ver = geos_version().decode().split(' ')[0]
```
Source: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error

"No module named django.core.management" when launching python manage.py migrate
---
```bash
  Traceback (most recent call last):
  File "manage.py", line 9, in <module>
    from django.core.management import execute_from_command_line
ImportError: No module named django.core.management
```
It seems that Django is not installed, ensure it with pip freeze and ensure that you are in the virtualenv. Sometimes for obvious reasons, the venv could be broken. So in the last test you can consider to rebuild it with `virtualenv -p python3 env` `source env/bin/activate`

Contribution
---

The git repo is organized by the gitflow organization scheme. Please see [this page](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) for more details on feature branches.

Issues are also tracked here. They are in no way definitive and are subject to change when the need arises.

# PowerMarket-Django
