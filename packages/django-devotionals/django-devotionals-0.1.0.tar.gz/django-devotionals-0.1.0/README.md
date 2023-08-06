Django devotionals
================== 

A demo application created as part of the 5Q programming challenge. The app handles the input and display of daily devotionals, including a django management command to import a csv file loaded with devotionals.

Install
---------

If the project were uploaded to pypi, it would be a simple:

```
pip install django-devotionals
```

But it's not, so don't try.

Else you could follow whatever procedure you use to install python packakges (easy_install, etc)

Configuration
--------------

Currently there is little to configure. The important part is to wire it up in your django project:

```
INSTALLED_APPS = (
    ...
    'devotionals',
    ...
)
```

In your urls:

```
urlpatterns += patterns('',
    ...
    (r'^devotionals/', include('devotionals.urls')),
    ...
)
```

Templates (& URLs)
--------------------

All templates go in a 'devotionals' directory in your TEMPLATE_DIR:

```
devotional_list.html (/)

devotional_year_archive.html (/<YYYY>/)

devotional_month_archive.html (/<YYYY>/<MMM>/)

devotional_detail.html (/<YYYY>/<MMM>/<DD>/)
```
