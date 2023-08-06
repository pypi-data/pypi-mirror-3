import os

from django.conf import settings
from django import forms
from django.template import Template, Context
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils.html import strip_spaces_between_tags

from djc.formrenderingtools.settings import DEFAULT_SETTINGS


class ContactForm(forms.Form):
    """
    A sample form, for use in test cases.
    """
    subject = forms.CharField(
        label='Subject',
        max_length=100,
    )
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(
        required=False,
        help_text='Send a copy of the message to the sender.',
    )
    
    def clean(self):
        """This sample form never validates!"""
        raise forms.ValidationError('Sorry, this sample form never validates!')


class FormLayoutsTestCase(TestCase):
    """
    Tests the "form_layouts" template tag library.
    
    Alters settings.TEMPLATE_DIRS so that only the original formrendering tools
    templates are available. Otherwise, the project's templates could interfere
    with test results.
    """
    def setUp(self):
        # Template directory: contains test templates
        # Form layouts template directory: contains test layouts
        #template_setting = ''
        #default_template_dir = DEFAULT_SETTINGS[template_setting]
        #self.form_layouts_template_dir = os.path.join(self.template_dir, 
        #                                              default_template_dir)
        self._change_settings()
    
    def tearDown(self):
        self._restore_settings()
    
    def _change_settings(self):
        """
        Loads default settings, so that the project configuration does not
        affects the test process.
        """
        template_dirs = (
          os.path.join(os.path.dirname(__file__), 'templates'),
          os.path.join(os.path.dirname(__file__), 'templates/tests/formrenderingtools'),
        )
        self.previous_settings = {}
        for key, value in DEFAULT_SETTINGS.iteritems():
            self.previous_settings[key] = getattr(settings, key) 
            setattr(settings, key, value)
        #template_setting = 'FORMRENDERINGTOOLS_TEMPLATE_DIR'
        setattr(settings, 'TEMPLATE_DIRS', template_dirs)
    
    def _restore_settings(self):
        """
        Restores the settings that were in use before running this test suite.
        """
        for key, value in self.previous_settings.iteritems():
            setattr(settings, key, value)
    
    def test_template_names(self):
        """Tests ElementNode.template_names().
        
        If this test fails, then most of the other tests may fail since the 
        templates will not be found.
        """
        from djc.formrenderingtools.templatetags import form_layouts
        
        fixtures = (
            # (element, layouts, templates, theoric_output)
            # Defaults
            ('form', None, None,
             ['form_layouts/default/form/default.html']),
            ('form', 'default', None,
             ['form_layouts/default/form/default.html']),
            ('form', None, 'default.html',
             ['form_layouts/default/form/default.html']),
            ('form', 'default', 'default.html',
             ['form_layouts/default/form/default.html']),
            # Element name
            ('form_errors', None, None,
             ['form_layouts/default/form_errors/default.html']),
            ('field_list', None, None,
             ['form_layouts/default/field_list/default.html']),
            # Layout names
            ('form', ('one', 'two', 'three'), None,
             ['form_layouts/one/form/default.html',
              'form_layouts/two/form/default.html',
              'form_layouts/three/form/default.html',
              'form_layouts/default/form/default.html']),
            # ... explicit priority for default layout
            ('form', ('one', 'default', 'two'), None,
             ['form_layouts/one/form/default.html',
              'form_layouts/default/form/default.html',
              'form_layouts/two/form/default.html']),
            # ... a layout name is, in fact, a directory name
            ('form', 'some/path/to/layout', None,
             ['form_layouts/some/path/to/layout/form/default.html',
              'form_layouts/default/form/default.html']),
            # Template names
            ('form', None, ('one.html', 'two.html', 'three.html'),
             ['form_layouts/default/form/one.html',
              'form_layouts/default/form/two.html',
              'form_layouts/default/form/three.html',
              'form_layouts/default/form/default.html']),
            # ... explicit priority for default template
            ('form', None, ('one.html', 'default.html', 'two.html'),
             ['form_layouts/default/form/one.html',
              'form_layouts/default/form/default.html',
              'form_layouts/default/form/two.html']),
            # ... a template name can contain sub-directories
            ('form', None, 'some/path/to/template.html',
             ['form_layouts/default/form/some/path/to/template.html',
              'form_layouts/default/form/default.html']),
            # Both layout and template names: template names priority
            ('form', ('one', 'two'), ('three.html', 'four.html'),
             ['form_layouts/one/form/three.html',
              'form_layouts/two/form/three.html',
              'form_layouts/default/form/three.html',
              'form_layouts/one/form/four.html',
              'form_layouts/two/form/four.html',
              'form_layouts/default/form/four.html',
              'form_layouts/one/form/default.html',
              'form_layouts/two/form/default.html',
              'form_layouts/default/form/default.html']),
        )
        for element, layouts, templates, theoric_output in fixtures:
            form_element = form_layouts.FormElementNode(element)
            real_output = list(form_element.template_names(layout_names=layouts, 
                                                           template_names=templates))
            self.assertEquals(theoric_output, real_output)
    
    def _render_string_to_string(self, template_code, context):
        """
        Renders template code to a string and removes some whitespaces, so that
        the comparison between theoric output and effective one can be compared
        with more flexibility.
        
        This fits HTML needs. You may not use it for any "whitespace sensitive"
        code.
        """
        t = Template(template_code)
        c = Context(context)
        return strip_spaces_between_tags(t.render(c)).strip()
    
    def _test_template_output(self, code, context):
        """
        Renders a template /form_layouts/<code>_source.html with the given
        context and validates that it matches the content of the
        /form_layouts/<code>_output.html file.
        """
        self.maxDiff = None # Django 1.3
        theory = render_to_string('%s_output.html' % code, context)
        theory = strip_spaces_between_tags(theory).strip()
        reality = render_to_string('%s_source.html' % code, context)
        reality = strip_spaces_between_tags(reality).strip()
        self.assertEquals(reality, theory)
    
    def test_template_dir_setting(self):
        """
        Tests the FORMRENDERINGTOOLS_TEMPLATE_DIR setting.
        """
        form = ContactForm()
        
        # Setting FORMRENDERINGTOOLS_TEMPLATE_DIR to something which does not
        # exist must raise an exception
        setattr(settings, 'FORMRENDERINGTOOLS_TEMPLATE_DIR', 'wrong_directory')
        try:
            self._render_string_to_string(
                '{% load form_layouts %}{% form %}',
                {'form': form},
            )
        except:
            pass
        else:
            self.fail('The FORMRENDERINGTOOLS_TEMPLATE_DIR has no effect')
        
        # Setting FORMRENDERINGTOOLS_TEMPLATE_DIR to something which exists
        # must work.
        # The "default test form layout" begins with a specific text
        # which is not in the "default production form layout". This text
        # is used to make sure that the test templates are used rather than the
        # default ones.
        setattr(settings, 'FORMRENDERINGTOOLS_TEMPLATE_DIR', 'form_layouts')
        test_text = u'<p>This is a test template for ' \
                    u'djc.formrenderingtools</p>'
        output = self._render_string_to_string(
            '{% load form_layouts %}{% form %}',
            {'form': form, 'test_text': test_text},
        )
        self.assertTrue(output.startswith(test_text))
    
    def _test_form_template(self, tag_name):
        """
        Sets up a form, render a template and assert it matches the expected
        output.
        """
        default_form = ContactForm()
        error_form = ContactForm({'subject': u'test'})
        context = {'form': default_form,
                   'error_form': error_form,
                   }
        self._test_template_output(tag_name, context)
    
    def test_templates(self):
        """Tests output of several use cases via templates."""
        use_cases = ('form', 'field_list', 'field', 'label', 'as_ul', 'as_p',
                     'as_table')
        for use_case in use_cases:
            self._test_form_template(use_case)
