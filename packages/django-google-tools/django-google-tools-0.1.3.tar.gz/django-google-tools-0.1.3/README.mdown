Google Analytics for Django Projects
====================================

## Installation

1. Add `googletools` to your `INSTALLED_APPS`
2. Run `./manage.py migrate` (or `./manage.py syncdb` if you do not make use of
   South)


## Management

Go to the admin interface. When correctly installed, you will find the
*Googletools* app. Here you can manage your Google Analytics and Site Verification
codes.


## Templatetags

In order to use the googletools in your templates you'll have to load the templatetags.

`{% load googletools %}`

### Google Analytics

Use `{% analytics_code %}` for inserting your Analytics code. This will return
an empty string when no code is setup for the current site.

### Google Site Verification

Use `{% site_verification_code %}` for inserting your site verification code.
This will return an empty string when no code is setup for the current site.
