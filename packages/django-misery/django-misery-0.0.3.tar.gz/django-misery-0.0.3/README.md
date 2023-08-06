# django-misery

## Overview

A simple ban system for Django, that does nasty stuff to trolls wandering on your website.

Users banned the classical way are encouraged to bypass the ban by creating another account or changing their IP address.
A nastier and probably more effective way to do it is to use what is known as slowban, and errorban. This Django middleware implements those.

### Features

* slowing page generation for miserable users
* logging them out randomly
* send a 404 from time to time...
* ... or a 403...
* ... or even a blank page if you want
* last but not least, a wonderful ASP.NET error page made just for them

Hey, they deserved it!

### Pros:

* lightweight, designed not to slow down your website a single bit (from a non-miserable point of view, of course)
* supports both IPv4 and IPv6

### Cons:

* doesn't currently support masks. Yes, it can be handy against users having a botnet under their control or in case of a user having an IPv6 range, but the current implementation favors speed over features.

## Installation & configuration

To install the app, you can use PIP: `pip install django-misery`; then add `django_misery` to your INSTALLED_APPS setting, and `django_misery.middleware.miserize` to your MIDDLEWARE_CLASSES.

The following settings can be personnalized:

* `MISERY_SLOW_STRENGTH`: seconds that miserable users will have to wait _at least_ (maximum twice longer) (default: 6)
* `MISERY_LOGOUT_PROBABILITY`: **percentage** of probability a user will be disconnected (default: 10)
* `MISERY_403_PROBABILITY`: same for 403 (default: 10)
* `MISERY_404_PROBABILITY`: I'm gonna let you guess for this one (default: 10)
* `MISERY_WHITE_SCREEN_PROBABILITY`: same for a nice, 100% pure white (not a single subpixel in the viewport will be off, I promise) (default: 10)
* `MISERY_ASP_ERROR_PROBABILITY`: a free bonus for ASP lovers (and I'm sure there are plenty around here), the template renders just great. Oh and: to make it even more beautiful, it's in French (default: 10). Quick preview:

![ASP error overview](http://img11.hostingpics.net/pics/560987ASPerror.png)

By default, miserable users have approximately a 50-50 chance to see the real page. They won't stay long, I promise.

## Miscellaneous

Inspired by the [Drupal Misery module](http://drupal.org/project/misery), see also ["Suspension, Ban or Hellban?"](http://www.codinghorror.com/blog/2011/06/suspension-ban-or-hellban.html) for hellbanning.
