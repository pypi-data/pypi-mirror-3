==================
Django Peer Review
==================

Version : 0.1.0
Author : Thomas Weholt <thomas@weholt.org>
License : Modified BSD
WWW : https://bitbucket.org/weholt/django-peer-review
Status : Beta

Django Peer Review is a reusable app for management of peer based reviews of arbitrary django models. It consists of a backend
 using the normal django admin and a frontend based on bootstrap from the guys behind Twitter.

**NB!** This is alpha/pre-beta software and the structure of the code WILL change until marked as stable.

Changelog
=========

0.1.0 - Initial release


Requirements
============

* django 1.4+


Installation
============

* pip install django-peer-review
* or download the source distro and do python setup.py install
* add 'peerreview' to INSTALLED_APPS in settings.py
* add "url(r'^peerreview/', include('peerreview.urls'))," to urls.py for your project
* for every model you want to use in reviews, create a template looking like::

    {% extends "peerreview/frontend/item_list.html" %}

* following the pattern of "templates/appname/modelname_peerreview.html"
