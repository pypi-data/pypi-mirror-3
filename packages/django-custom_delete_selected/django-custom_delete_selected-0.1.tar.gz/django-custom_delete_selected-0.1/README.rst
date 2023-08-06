Custom delete_selected action
=============================

Django ``delete_selected`` action in ``ModelAdmin`` not allow
you to add operations before and after deleting objects from
database by default.


Problem
-------

Default ``delete_selected`` action using ``delete`` method of queryset
so need to use ``pre_delete`` and ``post_delete`` signals.


Solution
--------

Disable_ ``delete_selected`` action for all applications and
models, but for some models this is crazy.


Installing
----------

The easiest way to install package is with pip!

You can install from PyPI (for Django==1.4)::

    $ pip install django-custom_delete_selected

Or GitHub for Django==1.4::

    $ pip install -e git+https://github.com/saippuakauppias/django-custom_delete_selected.git@django_v1.4#egg=custom_delete_selected

Or GitHub for Django==1.3.x::

    $ pip install -e git+https://github.com/saippuakauppias/django-custom_delete_selected.git@django_v1.3.x#egg=custom_delete_selected

Or from source::

    $ git clone https://github.com/saippuakauppias/django-custom_delete_selected.git
    $ cd django-custom_delete_selected
    $ python setup.py install


Usage
-----

Import ``custom_delete_selected.admin.CustomDeleteSelected`` to extend 
ModelAdmin class and override ``delete_model`` method. 
For example::

    from django.contrib import admin
    from custom_delete_selected.admin import CustomDeleteSelected
    
    
    class MyModelAdmin(CustomDeleteSelected, admin.ModelAdmin):

        # your code

        def delete_model(self, request, obj):
            # pre delete operations
            super(MyModelAdmin, self).delete_model(request, obj)
            # post delete operations

This code allow extends you deleting one object (when delete from change_form)
and same objects (when delete from change_list).


Contributing
------------

Feel free to fork, send pull requests or report bugs and issues on github.


.. _Disable: https://docs.djangoproject.com/en/1.3/ref/contrib/admin/actions/#django.contrib.admin.AdminSite.disable_action