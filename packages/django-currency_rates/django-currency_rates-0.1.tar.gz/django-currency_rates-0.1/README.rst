=====================
django-currency-rates
=====================

Django currencies and exchange rates for django projects

Features
========

- Currencies and exchange rates models
- Eschange rates with diferent rates for diferent dates
- Load automatically curencies and rates from http://openexchangerates.org/


Installation
============

#. Add ``"currency_rates"`` directory to your Python path.
#. Add ``"currency_rates"`` to the ``INSTALLED_APPS`` tuple found in
   your settings file.
#. Run ``manage.py syncdb`` to create the new tables
#. Run ``manage.py load_currencies`` to load currencies from http://openexchangerates.org/
#. Run ``manage.py load_rates`` to load current eschange rates from http://openexchangerates.org/





