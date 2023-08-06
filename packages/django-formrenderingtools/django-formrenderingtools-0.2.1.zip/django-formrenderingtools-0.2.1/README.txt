#########################
django-formrenderingtools
#########################

django-formrenderingtools is an application for the `Django framework
<http://www.djangoproject.com/>`_.
It provides tools for the template designer to customize forms.

Rather than using {{ form.as_p }}, set up and reuse templates to render 
Django's form elements.

For the impatient, use the bundled demo project to discover and try the
application (see docs/demo.txt for details).

This application provides a "form_layouts" template tag library
which itself provides the following template tags:

* form: renders a full form, i.e. non field errors, all fields, field
  errors, labels and help texts
* form_errors: renders global form errors, i.e. non field errors
* field_list: renders a set of fields in a form, with corresponding 
  field errors, labels and help texts
* field: renders a field, with field errors, label and help text
* field_errors: renders errors related to a field
* label: renders a field's label
* help_text: renders a field's help text

The goal of this application is to provide a pack of template tags which helps
you render each element of a form: full form, list of fields, non field errors 
(global errors), field errors (specific errors), field, label, help text...

Every form element has a corresponding template tag, which uses templates to
generate the output. Template designers no longer rely on developers to 
customize the form output.

This application uses a template-naming system that lets you reuse generic 
templates or use specific ones, depending on your needs. You can reuse built-in 
templates, override them or create your own templates.

*****
Links
*****

HTML documentation
  Browse the HTML documentation online at 
  http://packages.python.org/django-formrenderingtools/

RestructuredText documentation
  Read the RestructuredText documentation in the docs/ folder in the source
  code

Source code repository
  Follow the project on BitBucket at
  http://bitbucket.org/benoitbryon/django-formrenderingtools

Pypi
  The project is known as "django-formrenderingtools" in the Python package
  index. See http://pypi.python.org/pypi/django-formrenderingtools

*******************
Credits and license
*******************

This application is published under the BSD license. See 
`docs/LICENSE.txt <http://packages.python.org/django-formrenderingtools/LICENSE.html>`_
for details.
