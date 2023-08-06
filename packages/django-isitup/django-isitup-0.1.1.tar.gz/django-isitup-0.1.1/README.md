Django Is It Up 
================== 

Is it up is a fairly straight forward app that takes on the task of checking
web services to see if they are up and running. At the moment, the only goal
is to have it checking http services and sending out emails if an error code
is reached at a specified url.


Install
---------

```
pip install django-isitup
```

Else you could follow whatever procedure you use to install python packakges (easy_install, etc)

Configuration
--------------

Currently there is little to configure. The important part is to wire it up in your django project:

```
INSTALLED_APPS = (
    ...
    'isitup',
    ...
)
```

In your urls:

```
urlpatterns += patterns('',
    ...
    (r'^<your hook>/', include('isitup.urls')),
    ...
)
```

Templates (& URLs)
--------------------

All templates go in a 'isitup' directory in your TEMPLATE_DIR:

```
service_list.html (/)

service_create.html (/create/)

service_detail.html (/<slug>/)

service_edit.html (/<slug>/edit/)

```
