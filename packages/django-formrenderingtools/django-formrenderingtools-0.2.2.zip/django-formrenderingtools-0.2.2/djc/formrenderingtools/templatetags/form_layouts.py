import os.path

from django import template
from django.template import loader

from templateaddons.utils import decode_tag_arguments, parse_tag_argument

from django.conf import settings


register = template.Library()


class ElementNode(template.Node):
    """Base class for template tags of the "form_layouts" library.
    
    Subclasses must have an "element" property.
    """
    def template_names(self, layout_names=None, template_names=None):
        """Returns a generator over template names. Used by render() to select 
        the most accurate template.
        
        The returned generator contains values which look like the following:
        
        * "<layouts_dir>/<layout>/<element>/<template>"
        * "<layouts_dir>/<default_layout>/<element>/<template>"
        * "<layouts_dir>/<layout>/<element>/<default_template>"
        * "<layouts_dir>/<default_layout>/<element>/<default_template>"
        
        Where:
        
        * <layouts_dir> is settings.FORMRENDERINGTOOLS_TEMPLATE_DIR
        * <layout> is a value in given layout names
        * <default_layout> is settings.FORMRENDERINGTOOLS_DEFAULT_LAYOUT
        * <element> is the form element name, i.e. one in:
        
          * "form"
          * "form_errors"
          * "field_list"
          * "field"
          * "field_errors"
          * "label"
          * "help_text"
        
        * <template> is a value in given template names.
        
        It means that provided template name has higher priority than layout
        name.
        """
        if not layout_names:
            layout_names = []
        elif isinstance(layout_names, basestring):
            layout_names = [layout_names]
        if not template_names:
            template_names = []
        elif isinstance(template_names, basestring):
            template_names = [template_names]
        if not settings.FORMRENDERINGTOOLS_DEFAULT_LAYOUT in layout_names:
            layout_names = list(layout_names)
            layout_names.append(settings.FORMRENDERINGTOOLS_DEFAULT_LAYOUT)
        if not settings.FORMRENDERINGTOOLS_DEFAULT_TEMPLATE in template_names:
            template_names = list(template_names)
            template_names.append(settings.FORMRENDERINGTOOLS_DEFAULT_TEMPLATE)
        for template_name in template_names:
            for layout_name in layout_names:
                yield os.path.join(settings.FORMRENDERINGTOOLS_TEMPLATE_DIR,
                                   layout_name,
                                   self.element,
                                   template_name)


class FormElementNode(ElementNode):
    """Renders non-field elements, such as form, field list, form errors..."""
    def __init__(self, element, form=None, layout=None, fields=None, 
                 exclude_fields=None, template=None):
        self.element = element
        self.form = form
        self.layout = layout
        self.fields = fields
        self.exclude_fields = exclude_fields
        self.template_name = template
    
    def render(self, context):
        top_level_element = ('_form_layouts' not in context)
        if top_level_element:
            if not self.form:
                self.form = 'form'
            if not self.layout:
                self.layout = None
            if not self.template_name:
                self.template_name = None
        else:
            self.form = 'form'
            self.layout = 'layout'
            self.fields = 'fields'
            self.exclude_fields = 'exclude_fields'
            self.template_name = None
        
        form = parse_tag_argument(self.form, context)
        layout = parse_tag_argument(self.layout, context)
        fields = parse_tag_argument(self.fields, context)
        exclude_fields = parse_tag_argument(self.exclude_fields, context)
        template_name = parse_tag_argument(self.template_name, context)
        
        if self.element == 'field_list':
            if fields:
                if isinstance(fields, basestring):
                    fields = fields.split(',')
            else:
                fields = [field.name for field in form] # default field list
            if exclude_fields:
                if isinstance(exclude_fields, basestring):
                    exclude_fields = exclude_fields.split(',')
            else:
                exclude_fields = []
            fields = [field for field in fields if field not in exclude_fields]
            tmp = []
            for field_name in fields:
                for field in form:
                    if field.name == field_name:
                        tmp.append(field)
                        break
            fields = tmp
        
        template_names = self.template_names(layout, template_name)
        template_object = loader.select_template(template_names)
        
        context.push()
        context['_form_layouts'] = True
        context['form'] = form
        context['layout'] = layout
        context['fields'] = fields
        context['exclude_fields'] = exclude_fields
        output = template_object.render(context)
        context.pop()
        
        return output


def render_form_element(element, parser, token):
    default_arguments = {}
    default_arguments['form'] = None
    default_arguments['layout'] = None
    default_arguments['fields'] = None
    default_arguments['exclude_fields'] = None
    default_arguments['template'] = None
    arguments = decode_tag_arguments(token, default_arguments)
    
    return FormElementNode(element, **arguments)


@register.tag
def form(parser, token):
    return render_form_element('form', parser, token)


@register.tag
def form_errors(parser, token):
    return render_form_element('form_errors', parser, token)


@register.tag
def field_list(parser, token):
    return render_form_element('field_list', parser, token)


class FieldElementNode(ElementNode):
    """Renders elements at field level: field, field's errors, field's label, 
    field's help text...
    """
    def __init__(self, element, field=None, layout=None, template=None):
        self.element = element
        self.field = field
        self.layout = layout
        self.template_name = template
    
    def render(self, context):
        top_level_element = ('_form_layouts' not in context)
        if top_level_element:
            if not self.field:
                self.form = 'field'
            if not self.layout:
                self.layout = None
            if not self.template_name:
                self.template_name = None
        else:
            self.field = 'field'
            self.layout = 'layout'
            self.template_name = None
        
        field = parse_tag_argument(self.field, context)
        layout = parse_tag_argument(self.layout, context)
        template_name = parse_tag_argument(self.template_name, context)
        template_names = []
        if template_name:
            template_names.append(template_name)
        template_names.append('%s.html' % field.html_name)
        
        template_names = self.template_names(layout, template_names)
        template_object = loader.select_template(template_names)
        
        context.push()
        context['_form_layouts'] = True
        context['field'] = field
        context['field_id'] = field.field.widget.id_for_label(field.field.widget.attrs.get('id') or field.auto_id) # code from django/forms/forms.py, BoundField.label_tag()
        context['layout'] = layout
        context['template'] = template_name
        output = template_object.render(context)
        context.pop()
        
        return output


def render_field_element(element, parser, token):
    default_arguments = {}
    default_arguments['field'] = None
    default_arguments['layout'] = None
    default_arguments['template'] = None
    arguments = decode_tag_arguments(token, default_arguments)
    
    return FieldElementNode(element, **arguments)


@register.tag
def field(parser, token):
    return render_field_element('field', parser, token)


@register.tag
def field_errors(parser, token):
    return render_field_element('field_errors', parser, token)


@register.tag
def label(parser, token):
    return render_field_element('label', parser, token)


@register.tag
def help_text(parser, token):
    return render_field_element('help_text', parser, token)


"""Deprecated template tags. They still exist for backward compatibility."""

@register.tag
def render_form(*args, **kwargs):
    """Deprecated. See form().
    
    Exists for backward compatibility.
    """
    return form(*args, **kwargs)


@register.tag
def render_form_errors(*args, **kwargs):
    """Deprecated. See form_errors().
    
    Exists for backward compatibility.
    """
    return form_errors(*args, **kwargs)


@register.tag
def render_field_list(*args, **kwargs):
    """Deprecated. See field_list().
    
    Exists for backward compatibility.
    """
    return field_list(*args, **kwargs)


@register.tag
def render_field(*args, **kwargs):
    """Deprecated. See field().
    
    Exists for backward compatibility.
    """
    return field(*args, **kwargs)


@register.tag
def render_field_errors(*args, **kwargs):
    """Deprecated. See field_errors().
    
    Exists for backward compatibility.
    """
    return field_errors(*args, **kwargs)


@register.tag
def render_label(*args, **kwargs):
    """Deprecated. See label().
    
    Exists for backward compatibility.
    """
    return label(*args, **kwargs)


@register.tag
def render_help_text(*args, **kwargs):
    """Deprecated. See help_text().
    
    Exists for backward compatibility.
    """
    return help_text(*args, **kwargs)
