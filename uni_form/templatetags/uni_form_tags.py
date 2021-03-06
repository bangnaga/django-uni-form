# -*- coding: utf-8 -*-
from django.forms.formsets import BaseFormSet
from django.template import Context
from django.template.loader import get_template
from django import template

from uni_form.helpers import FormHelper

register = template.Library()
# We import the filters, so they are available when doing load uni_form_tags
from uni_form_filters import *

############################################################################
#
# Everything from now on gets more fancy
# It can be argued that having django-uni-form construct your forms is overkill
# and that I am playing architecture astronaut games with form building.
#
# However, all the bits that follow are designed to be section 508 compliant,
# so all the fancy JS bits are garanteed to degrade gracefully.
#
############################################################################

class BasicNode(template.Node):
    """ 
    Basic Node object that we can rely on for Node objects in normal
    template tags. I created this because most of the tags we'll be using
    will need both the form object and the helper string. This handles
    both the form object and parses out the helper string into attributes
    that templates can easily handle.
    """
    def __init__(self, form, helper):
        self.form = template.Variable(form)
        if helper is not None:
            self.helper = template.Variable(helper)
        else:
            self.helper = None

    def get_render(self, context):
        """ 
        Returns a `Context` object with all the necesarry stuff for rendering the form

        :param context: `django.template.Context` variable holding the context for the node

        `self.form` and `self.helper` are resolved into real Python objects resolving them
        from the `context`. 
        The `actual_form` can be a form or a formset. If it's a formset `is_formset` is set to True.
        If the helper has a layout we use it, for rendering the form or the formset's forms.
        """
        actual_form = self.form.resolve(context)
        attrs = {}
        if self.helper is not None:
            helper = self.helper.resolve(context)

            if not isinstance(helper, FormHelper):
                raise TypeError('helper object provided to uni_form tag must be a uni_form.helpers.FormHelper object.')
            attrs = helper.get_attributes()
        else:
            helper = None

        # We get the response dictionary 
        is_formset = isinstance(actual_form, BaseFormSet)
        response_dict = self.get_response_dict(attrs, context, is_formset)

        # If we have a helper's layout we use it, for the form or the formset's form
        if helper and helper.layout:
            if not is_formset:
                actual_form.form_html = helper.render_layout(actual_form, attrs['form_style'])
            else:
                for form in actual_form.forms:
                    form.form_html = helper.render_layout(form, attrs['form_style'])

        if is_formset:
            response_dict.update({'formset': actual_form})
        else:
            response_dict.update({'form': actual_form})

        return Context(response_dict)

    def get_response_dict(self, attrs, context, is_formset):
        """
        Returns a dictionary with all the parameters necessary to render the form/formset in a template.
        
        :param attrs: Dictionary with the helper's attributes used for rendering the form/formset
        :param context: `django.template.Context` for the node
        """
        form_type = "form"
        if is_formset:
            form_type = "formset"

        # We take form/formset parameters from attrs if they are set, otherwise we use defaults
        response_dict = {
            '%s_action' % form_type: attrs.get("form_action", '.'),
            '%s_method' % form_type: attrs.get("form_method", 'post'),
            '%s_tag' % form_type: attrs.get("form_tag", True),
            '%s_class' % form_type: attrs.get("class", ''),
            '%s_id' % form_type: attrs.get("id", ""),
            'form_error_title': attrs.get("form_error_title", None),
            'formset_error_title': attrs.get("formset_error_title", None),
            'inputs': attrs.get('inputs', []),
            'is_formset': is_formset,
        }

        if context.has_key('csrf_token'):
            response_dict['csrf_token'] = context['csrf_token']

        return response_dict


class UniFormNode(BasicNode):
    def render(self, context):
        c = self.get_render(context)

        if c['is_formset']:
            template = get_template('uni_form/whole_uni_formset.html')
        else:
            template = get_template('uni_form/whole_uni_form.html')

        return template.render(c)


# {% uni_form %} tag
@register.tag(name="uni_form")
def do_uni_form(parser, token):
    """
    You need to pass in at least the form object, and can also pass in the
    optional helper object. Writing the attrs string is rather challenging so
    use of the objects found in uni_form.helpers is encouraged.

    form: The forms object to be rendered by the tag

    helper (optional): A uni_form.helpers.FormHelper object.

    Usage::
    
        {% include uni_form_tags %}

        {% uni_form my-form my_helper %}

    """
    token = token.split_contents()
    form = token.pop(1)

    try:
        helper = token.pop(1)
    except IndexError:
        helper = None

    return UniFormNode(form, helper)
