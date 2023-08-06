import os.path

from django.core.urlresolvers import reverse
from django.template.loader import find_template
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template

from demo.demoapp.forms import FakeContactForm


def get_template_string(template_name):
    """Utility method that returns the source code of the given template name.

    Template filenames are relative to the demoapp templates folder."""
    base_path = os.path.dirname(__file__)
    filename = os.path.join(base_path, 'templates', template_name)
    with open(filename) as f:
        return f.read()


def demo_page(request, title, description, form, template):
    """Old-style generic view to display a demo page."""
    context_data = {
        'title': title,
        'description': description,
        'form': form,
        'template': template,
    }
    context_data['source'] = get_template_string(context_data['template'])
    template_name = 'demoapp/demo.html'
    return direct_to_template(request, template_name, context_data)


def comparison_page(request, title, description, form, template):
    """Old-style generic view to display a comparison page."""
    context_data = {
        'title': title,
        'description': description,
        'form': form,
        'builtin_template': 'demoapp/includes/%s_builtin.html' % template,
        'formrenderingtools_template': 'demoapp/includes/%s_formrenderingtools.html' % template,
    }
    context_data['builtin_source'] = get_template_string(context_data['builtin_template'])
    context_data['formrenderingtools_source'] = get_template_string(context_data['formrenderingtools_template'])
    template_name = 'demoapp/comparison.html'
    return direct_to_template(request, template_name, context_data)


def simple(request):
    title = _("Simplest way to display a form")
    description = _("The following example illustrates the minimal way to display a form.")
    form = FakeContactForm()
    template = 'simple'
    return comparison_page(request, title, description, form, template)


def errors(request):
    title = _("Displaying form errors")
    description = _("Let's see what happens with an invalid form. Notice that nothing changed in both template code.")
    form = FakeContactForm({'subject': u''})
    template = 'errors'
    return comparison_page(request, title, description, form, template)


def as_table(request):
    title = _("Reproducing form.as_table")
    description = _("Want to reproduce some form.as_table behaviour for backward compatibility? No problem! Notice that 'as_table' is the default for Django builtins, so {% form layout='as_table' %} reproduces both {{ form }} and {{ form.as_table }}.")
    form = FakeContactForm({'subject': u''})
    template = 'as_table'
    return comparison_page(request, title, description, form, template)


def as_ul(request):
    title = _("Reproducing form.as_ul")
    description = _("Want to reproduce some form.as_ul behaviour for backward compatibility? No problem!")
    form = FakeContactForm({'subject': u''})
    template = 'as_ul'
    return comparison_page(request, title, description, form, template)


def as_p(request):
    title = _("Reproducing form.as_p")
    description = _("Want to reproduce some form.as_p behaviour for backward compatibility? No problem!")
    form = FakeContactForm({'subject': u''})
    template = 'as_p'
    return comparison_page(request, title, description, form, template)


def fields_order(request):
    title = _("Reordering fields")
    description = _("""Often, you don't want to reoder fields in Python code because:</p>
<ul>
  <li>it resides in Django,</li>
  <li>or in a third party module (don't want to fork it!),</li>
  <li>or it is a ModelForm (don't want to alter the model).</li>
</ul>
<p>Reordering form fields in a Django template is boring: you have to reproduce all the template code for each field! And don't forget error messages, help texts...</p>
<p>Notice that the field id in {{ field }} is computed with Python code. You cannot get it in templates to fill in the "for" property of the labels. This could become tricky if you are using form prefixes.</p>
<p>This example uses a ModelForm on django.contrib.sites.models.Site. We *just* want to display 'display name' before 'domain name'.</p>
<p>Maybe you are thinking that you had better include a template file instead of repeating code... That is exactly the purpose of Django-formrenderingtools ;)""")
    from django.contrib.sites.models import Site
    from django.forms import ModelForm
    class SiteForm(ModelForm):
        class Meta:
            model = Site
    form = SiteForm({'name': u'example'})
    template = 'fields_order'
    return comparison_page(request, title, description, form, template)


def fieldsets(request):
    title = _("Displaying fieldsets")
    description = _("""Form decomposition with Django builtins: you have to rewrite all fields manually... Need a {% field_list %} template tag?</p>
<p>In this example, we want to create two fieldsets: one to group message and subject, another one to group fields about sender.""")
    form = FakeContactForm()
    template = 'fieldsets'
    return comparison_page(request, title, description, form, template)


def two_custom_fields(request):
    title = _("Customizing specific fields in a form")
    description = _("""What if you want to customize only a few fields in a form?</p>
<p>In this example, we want to do two things:</p>
<ol>
  <li>change label of "message" field by "Your message"</li>
  <li>change order of field and label for "sender nickname" field</li>
</ol>
<p>What happened in the Django-formrenderingtools side?</p>
<ul>
  <li>we declared a new "form layout". It is the directory name of a set of templates.</li>
  <li>we created two template files in demo/demoapp/templates/form_layouts/two_custom_fields/</li>
  <li>one is called label/message.html</li>
  <li>the other is called field/sender_nickname.html</li>
  <li>the two templates were copied then adapted from djc/formrenderingtools/templates/form_layouts/default/...</li>
</ul>""")
    form = FakeContactForm()
    template = 'two_custom_fields'
    return comparison_page(request, title, description, form, template)


def altering_all_elements(request):
    title = _("Altering all elements at once for a specific form")
    description = _("""What if you want to customize all elements in a form?</p>
<p>In this example, we want to display field before label for each field.</p>
<p>What happened in the Django-formrenderingtools side?</p>
<ul>
  <li>we declared a new form layout: "altering_all_elements"</li>
  <li>we created a template file in demo/demoapp/templates/form_layouts/altering_all_elements/</li>
  <li>it is called field/default.html</li>
  <li>the templates was copied then adapted from djc/formrenderingtools/templates/form_layouts/default/field/default.html</li>
</ul>""")
    form = FakeContactForm()
    template = 'altering_all_elements'
    return comparison_page(request, title, description, form, template)
