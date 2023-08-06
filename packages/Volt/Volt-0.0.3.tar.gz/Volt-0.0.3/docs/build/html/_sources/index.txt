.. Volt documentation master file, created by
   sphinx-quickstart on Tue Apr 17 23:58:10 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Volt
===============

Volt is a general-purpose static website generator written in Python. It is:

- **Lightweight**

  Volt's absolute dependency is only Jinja2, the powerful Python-based
  templating language.

- **Modular**

  At its core, Volt is a collection of different Engines responsible for
  different sections of your site. Use only the ones you want and forget the
  rest. Two engines comes built-in with Volt: the Blog engine, for generating
  blogs, and the Plain engine, for generating simple standalone pages.

- **Extendable**

  Add functionalities to your site with Plugins and Widgets. Volt comes packed 
  with five built-in plugins: three for markup (Markdown, rSt, textile), one
  for generating atom feeds, and one for syntax highlighting.

- **Flexible**

  Configure everything from date and time formatting, how your contents should
  be paginated, to your own Jinja filters and tests. All can be done from
  Volt's central configuration file.

- **Themable**

  All style and template files are grouped in one place, enabling easy style
  switching.

- **And comes with extra goodies:**

  - Experimental Python 3 support.

  - Auto-regenerating web server.

  - Command line autocompletion script.

  - Logging support.
  
Can't wait to try? Install Volt now and see a live demo on your computer right
away::

    $ pip install volt
    $ mkdir volt-demo; cd volt-demo
    $ volt demo


Why Static Websites?
--------------------

1. **Ease of deployment**

   Static websites are essentially flat HTML files in a folder, no database
   required. This makes deployment as easy as copy-pasting files. Any modern web
   server will be able to serve static websites without requiring complex
   configuration.

2. **Speed**

3. **Security**

4. **Simple backup and versioning**


Contributing
------------

Fork the latest development version from `Github
<https://github.com/bow/volt>`_ and bootstrap the development environment
(`git <http://git-scm.com/>`_ and `pip <http://www.pip-installer.org/>`_
are required)::

    $ git clone https://github.com/bow/volt.git
    $ cd volt
    $ make dev

Report any bugs, feature request, or critiques to the `main issue tracker
<https://github.com/bow/volt/issues>`_. Or go straight to submitting your pull
requests.


.. include:: contents.rst.inc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
