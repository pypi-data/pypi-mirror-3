===================
Flask-Heroku-Runner
===================

Flask-Heroku-Runner
===================

*Quickly integrate your Flask application with the Heroku stack.*

Resources
=========

* `Documentation <http://flask-heroku-runner.readthedocs.org/>`_
  on *Read the Docs*
* `Source Code <http://bitbucket.org/daveshawley/flask-heroku-runner>`_
  in *Bit Bucket*

Install
=======

The easiest way to install is with `pip`_::

    $ pip install Flask-Heroku-Runner

You can also install from source using ``setup.py`` if you are that
type of person::

    $ python setup.py install


Usage
=====

Simply import the extension and use
:py:class:`flask.ext.heroku_runner.HerokuApp` in place of
:py:class:`flask.Flask`.

What you get
------------

``HerokuApp`` is a sub-class of :py:class:`flask.Flask` that recognizes the
``HOST`` and ``PORT`` environment variables that the Heroku stack provides
and configures the application to use them.

API Reference
=============

.. py:class:: flask.ext.heroku_runner.HerokuApp(*positional, **keywords)

   Simple wrapper for :py:class:`flask.Flask` that integrates nicely with
   the Heroku Python stack.

   .. py:method:: run(*positional, **keywords)

      Inserts the ``HOST`` and ``PORT`` environment variable values into
      ``keywords`` using the keys ``host`` and ``port`` and then calls
      :py:meth:`flask.Flask.run` using the arguments.  If the environment
      variables are not set, then this method is a simple pass through.


Changelog
=========

* Version 1

  Initial release.


.. _`pip`: http://www.pip-installer.org/

