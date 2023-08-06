
django-redactorjs
===============
http://github.com/TigorC/django-redactorjs


What's that
-----------

*django-redactorjs is a reusable application for Django, using WYSIWYG editor http://redactorjs.com/*

Dependence
-----------

- Django >= 1.3 # for static files
- PIL # for image upload

Getting started
-----------

* Install django-redactorjs:

``pip install django-redactorjs
``

* Add `'redactor'` to INSTALLED_APPS.

* Add `url(r'^redactor/', include('redactor.urls'))`, to urls.py

* Add default config in settings.py (more settings see: <http://redactorjs.com/docs/settings/>):

```REDACTOR_OPTIONS = {'lang': 'ru'}
REDACTOR_UPLOAD = 'uploads/'
```

Using in model
-----------

```python
from django.db import models
from redactor.fields import RedactorField

class Entry(models.Model):
    title = models.CharField(max_length=250, verbose_name=u'Заголовок')
    short_text = RedactorField(verbose_name=u'Краткий текст')
```

or use custom parametrs:
```short_text = RedactorField(verbose_name=u'Краткий текст',
                redactor_options={'lang': 'ru', 'focus': 'true'},
                upload_to='tmp/')
```