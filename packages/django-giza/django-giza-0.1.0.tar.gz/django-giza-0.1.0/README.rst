=====================
Django-Sphinx-autodoc
=====================


.. note::

    Original code is from https://github.com/Aquasys/django-sphinx-autodoc
    This version has been cleaned up and modified to work as a Django
    management command.


Django is very nice in that way you can reuse a lot of applications in your
projects. It means for big projects that you'll get a long list of applications
in your settings.INSTALLED_APP.

If you're using Django with Sphinx and want to autodoc all these apps in a wink
of an eye, then this app is for you.

A good combinaison for documenting your project would be:
 - **sphinx**
 - **django-sphinx-autodoc** to generate the doc from your applications
 - **django-sphinxdoc** to integrate the sphinx doc in your website


How it works
------------

It will scrape all your .py files in each application listed by INSTALLED_APP,
then add automodules in your PROJECT/SPHINX_ROOT/auto_modules.rst.

You will then see your applications grouped in 2 different categories:

- **internal application** is an application located in your project directory
- **external application** is an app which is somewhere in your pythonpath
  (preferably in your virtualenv)


Good Practices
--------------

Add a docstring in your application's ``\_\_init\_\_.py`` file to describe it.
django-sphinx-autodoc will automatically scrape it for you (although
``\_\_init.\_\_.py`` files are excluded by default)


Install
-------

``$ pip install django-sphinx-autodoc``


Usage
-----

``$ ./manage.py sphinx_autodoc``


Settings
--------

You can modify some of the settings used by django-sphinx-autodoc:

- **DS_ROOT**: root path for documentation, absolute path required (defaults to "PROJECT_ROOT/docs")
- **DS_MASTER_DOC**: name of your master document (defaults to "index.rst")
- **DS_FILENAME**: name for the modules (defaults to "auto_modules.rst")
- **DS_DOC_TITLE**: title for the modules page (defaults to "Python modules")
- **DS_EXCLUDED_APPS**: list of applications to exclude (defaults to [])
- **DS_EXCLUDED_MODULES**: list of files to exclude (default to ["\_\_init\_\_.py"])


TODO
----

- Write tests
- improve the not_relevant stuff to auto exclude a file without class or def
- Django command extension to update the autodoc
