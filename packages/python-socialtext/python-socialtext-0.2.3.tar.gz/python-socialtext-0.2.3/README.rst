Python bindings for the Socialtext REST API
===========================================

This is a client for Socialtext's REST API. The goal of this project is to provide an extensible library that helps you focus on building applications that leverage the power of Socialtext instead of worrying about HTTP methods and status codes.

You can read the documentation at:
http://python-socialtext.readthedocs.org/

.. contents:: Contents:
   :local:

Requirements
------------

1. requests-0.3.0__

__ http://pypi.python.org/pypi/requests


Installation
------------

You can install python-socialtext using pip or easy_install::

    pip install python-socialtext

    # or
    
    easy_install python-socialtext

The tests use nose__ and can be run using::

	python setup.py test

	# or

	nosetests

__ http://code.google.com/p/python-nose/

You can use Sphinx__ to build the documentation locally::

    cd docs
    make html # windows: use make.bat

    # open the _build/index.html document in your browser

__ http://sphinx.pocoo.org/

Python API
----------

Quick start::

    from socialtext import Socialtext

    st = Socialtext(url=ST_URL, username=USERNAME, password=PASSWORD)

    st.signals.create("This is a signal from the API!")
    <Signal: 1234>

    signal.delete()

    st.pages.list("ws-name")
    <Page: test_page>, <Page: test_page_2>, <Page: test_page_3>

    ws = st.workspaces.get("ws-name")
    st.pages.list(ws)
    <Page: test_page>, <Page: test_page_2>, <Page: test_page_3>

Contributing
------------

Development takes place on Github__. You can file bug reports and pull requests there.

__ https://github.com/hanover/python-socialtext

Branches
````````

This project follows the git-flow__ branch methodology. So, there will always be two branches in the repository:

    master
        The stable, production branch.
    
    develop
        Active development work towards the next release. All pull requests will be merged into this branch.

__ https://github.com/nvie/gitflow