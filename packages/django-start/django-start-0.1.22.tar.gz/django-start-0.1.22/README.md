Django-start installs a script which allows the easy creation of Django 
projects and applications based the layout used at RED Interactive Agency.

How to use
==========

An in-depth tutorial is available at: http://ff0000.github.com/2011/10/django-hands-on-tutorial/

Creating a project
------------------
  
    pip install django-start
    django-start.py project example
    
This will use the default project template, which includes 
[red-boilerplate](https://github.com/ff0000/red-boilerplate).

Running a project
-----------------

    cd example
    virtualenv env
    source env/bin/activate
    cd project
    python manage.py require
    python manage.py sync
    python manage.py server

<!--
Using a custom project template
-------------------------------

If you prefer to use a custom project template than the one included in
this application, create your custom project template directory and call the
command script like this:

    django-start.py --template-dir=/your/custom/template project new_example
-->

How to contribute
=================

Fork the project, make your changes, then run

    python test.py
    
This command will:

* create a test project using the `ff0000` template
* create a test app inside that project using the `blog` template
* run the test suite for the app

If everything runs correctly, then submit a pull request via Github.

You can have the tests run automatically before any commit by adding an executable file `.git/hooks/pre-commit` with this code:

    #!/bin/sh
    python test.py || exit 1
