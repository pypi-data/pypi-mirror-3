Introduction
============

Yet another `paste`_ factories for django

.. _paste: http://pythonpaste.org/

.. contents::

Makina Corpus sponsored software
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com



What is dj.paste
==================

It is just another `PythonPaste applications`_ wsgi wrappers:

.. _PythonPaste applications: http://pythonpaste.org/deploy/#paste-app-factory

    * ``dj.paste#mono`` or only ``dj.paste``:
        A paste factory to use when you have only one django on your instance

    * ``dj.paste#multi``
        A paste factory to use when you have more than one django on your instance 
        but be careful that there is a fakeDjangoModule trick that can lead to problems (not seen so far)


How to use dj.paste
=====================

Django App
----------------
With paste, just add another app entry with a django_settings_module  variable to point to
your django settings ::

    [composite:main]
    use = egg:Paste#urlmap
    / = foo

    [app:foo]
    use=egg:dj.paste
    django_settings_module=foo.settings 
