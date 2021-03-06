# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import get_template_from_string
from django.template.loader import render_to_string
from django.middleware.csrf import _get_new_csrf_key
from django.test import TestCase

from uni_form.helpers import FormHelper, FormHelpersException, Submit, Reset, Hidden, Button
from uni_form.helpers import Layout, Fieldset, MultiField, Row, Column, HTML


class TestForm(forms.Form):
    is_company = forms.CharField(label="company", required=False, widget=forms.CheckboxInput())
    email = forms.CharField(label="email", max_length=30, required=True, widget=forms.TextInput())
    password1 = forms.CharField(label="password", max_length=30, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label="re-enter password", max_length=30, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(label="first name", max_length=30, required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="last name", max_length=30, required=True, widget=forms.TextInput())

    def clean(self):
        super(TestForm, self).clean()
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)
        if not password1 and not password2 or password1 != password2:
            raise forms.ValidationError("Passwords dont match")

        return self.cleaned_data

class TestBasicFunctionalityTags(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_as_uni_errors_form_without_non_field_errors(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {{ form|as_uni_errors }}
        """)
        form = TestForm({'password1': "god", 'password2': "god"})
        form.is_valid()

        c = Context({'form': form})
        html = template.render(c)
        self.assertFalse("errorMsg" in html)

    def test_as_uni_errors_form_with_non_field_errors(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {{ form|as_uni_errors }}
        """)
        form = TestForm({'password1': "god", 'password2': "wargame"})
        form.is_valid()

        c = Context({'form': form})
        html = template.render(c)
        self.assertTrue("errorMsg" in html)
        self.assertTrue("<li>Passwords dont match</li>" in html)
        self.assertFalse("<h3>" in html)

    def test_as_uni_form(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {{ form|as_uni_form }}
        """)
        c = Context({'form': TestForm()})
        html = template.render(c)
        
        self.assertTrue("<td>" not in html)
        self.assertTrue("id_is_company" in html)
    
    def test_uni_form_setup(self):
        template = get_template_from_string("""
            {% load uni_form_tags %}
            {% uni_form_setup %}
        """)
        c = Context()
        html = template.render(c)
        
        # Just look for file names because locations and names can change.
        self.assertTrue('default.uni-form.css' in html)
        self.assertTrue('uni-form.css' in html)
        self.assertTrue('uni-form.jquery.js' in html)

class TestFormHelpers(TestCase):
    urls = 'uni_form.tests.urls'
    def setUp(self):
        pass
    
    def tearDown(self):
        pass    

    def test_uni_form_helper_inputs(self):
        form_helper = FormHelper()
        submit  = Submit('my-submit', 'Submit', css_class="button white")
        reset   = Reset('my-reset', 'Reset')
        hidden  = Hidden('my-hidden', 'Hidden')
        button  = Button('my-button', 'Button')
        form_helper.add_input(submit)
        form_helper.add_input(reset)
        form_helper.add_input(hidden)
        form_helper.add_input(button)
        
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)
        c = Context({'form': TestForm(), 'form_helper': form_helper})        
        html = template.render(c)

        # NOTE: Not sure why this is commented
        self.assertTrue('class="submit submitButton button white"' in html)
        self.assertTrue('id="submit-id-my-submit"' in html)        

        self.assertTrue('class="reset resetButton"' in html)
        self.assertTrue('id="reset-id-my-reset"' in html)        

        self.assertTrue('name="my-hidden"' in html)        

        self.assertTrue('class="button"' in html)
        self.assertTrue('id="button-id-my-button"' in html)        

    def test_invalid_helper_method(self):
        form_helper = FormHelper()
        try:
            form_helper.form_method = "superPost"
            self.fail("Setting an invalid form_method within the helper should raise an Exception")
        except FormHelpersException: 
            pass

    def test_uni_form_with_helper_attributes_without_layout(self):
        form_helper = FormHelper()    
        form_helper.form_id = 'this-form-rocks'
        form_helper.form_class = 'forms-that-rock'
        form_helper.form_method = 'GET'
        form_helper.form_action = 'simpleAction'
        form_helper.form_error_title = 'ERRORS'
    
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form testForm form_helper %}
        """)        

        # now we render it, with errors
        form = TestForm({'password1': 'wargame','password2': 'god'})
        form.is_valid()
        c = Context({'testForm': form, 'form_helper': form_helper})            
        html = template.render(c)
        
        # Lets make sure everything loads right
        self.assertTrue('<form' in html)
        self.assertTrue('class="uniForm forms-that-rock"' in html)
        self.assertTrue('method="get"' in html)
        self.assertTrue('id="this-form-rocks">' in html)
        self.assertTrue('action="%s"' % reverse('simpleAction') in html)

        self.assertTrue("<h3>ERRORS</h3>" in html)
        self.assertTrue("<li>Passwords dont match</li>" in html)

        # now lets remove the form tag and render it again. All the True items above
        # should now be false because the form tag is removed.
        form_helper.form_tag = False 
        html = template.render(c)        
        self.assertFalse('<form' in html)        
        self.assertFalse('class="uniForm forms-that-rock"' in html)
        self.assertFalse('method="get"' in html)
        self.assertFalse('id="this-form-rocks">' in html)

    def test_uni_form_without_helper(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form %}
        """)
        c = Context({'form': TestForm()})            
        html = template.render(c)        
        
        # Lets make sure everything loads right
        self.assertTrue('<form' in html)
        self.assertTrue('class="uniForm"' in html)
        self.assertTrue('method="post"' in html)
        self.assertTrue('action="."' in html)

    def test_uni_form_invalid_helper(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)
        c = Context({'form': TestForm(), 'form_helper': "invalid"})

        settings.UNIFORM_FAIL_SILENTLY = False
        if settings.TEMPLATE_DEBUG:
            self.assertRaises(TemplateSyntaxError, lambda:template.render(c))
        else:
            self.assertRaises(TypeError, lambda:template.render(c))
        del settings.UNIFORM_FAIL_SILENTLY

    def test_uni_form_formset(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form testFormSet formset_helper %}
        """)
        
        form_helper = FormHelper()    
        form_helper.form_id = 'thisFormsetRocks'
        form_helper.form_class = 'formsets-that-rock'
        form_helper.form_method = 'POST'
        form_helper.form_action = 'simpleAction'
                
        from django.forms.models import formset_factory
        TestFormSet = formset_factory(TestForm, extra = 3)
        testFormSet = TestFormSet()
        
        c = Context({'testFormSet': testFormSet, 'formset_helper': form_helper, 'csrf_token': _get_new_csrf_key()})
        html = template.render(c)        

        self.assertEqual(html.count('<form'), 1)
        self.assertEqual(html.count("<input type='hidden' name='csrfmiddlewaretoken'"), 1)

        self.assertTrue('class="uniForm formsets-that-rock"' in html)
        self.assertTrue('method="post"' in html)
        self.assertTrue('id="thisFormsetRocks">' in html)
        self.assertTrue('action="%s"' % reverse('simpleAction') in html)

    def test_CSRF_token_POST_form(self):
        form_helper = FormHelper()    
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        

        # The middleware only initializes the CSRF token when processing a real request
        # So using RequestContext or csrf(request) here does not work.
        # Instead I set the key `csrf_token` to a CSRF token manually, which `csrf_token` tag uses
        c = Context({'form': TestForm(), 'form_helper': form_helper, 'csrf_token': _get_new_csrf_key()})
        html = template.render(c)

        self.assertTrue("<input type='hidden' name='csrfmiddlewaretoken'" in html)                

    def test_CSRF_token_GET_form(self):
        form_helper = FormHelper()    
        form_helper.form_method = 'GET'
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        

        c = Context({'form': TestForm(), 'form_helper': form_helper, 'csrf_token': _get_new_csrf_key()})
        html = template.render(c)
        
        self.assertFalse("<input type='hidden' name='csrfmiddlewaretoken'" in html) 

class TestFormLayout(TestCase):
    def test_layout_invalid_unicode_characters(self):
        # Adds a BooleanField that uses non valid unicode characters "ñ"
        form = TestForm()
        
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                'españa'
            )
        )
        
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        c = Context({'form': TestForm(), 'form_helper': form_helper})
        settings.UNIFORM_FAIL_SILENTLY = False
        self.assertRaises(Exception, lambda:template.render(c))
        del settings.UNIFORM_FAIL_SILENTLY

    def test_layout_unresolved_field(self):
        form = TestForm()
        
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                'typo'
            )
        )

        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        c = Context({'form': TestForm(), 'form_helper': form_helper})
        settings.UNIFORM_FAIL_SILENTLY = False
        self.assertRaises(Exception, lambda:template.render(c))
        del settings.UNIFORM_FAIL_SILENTLY

    def test_double_rendered_field(self):
        form = TestForm()
        
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                'is_company', 'is_company'
            )
        )

        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        c = Context({'form': TestForm(), 'form_helper': form_helper})
        settings.UNIFORM_FAIL_SILENTLY = False
        self.assertRaises(Exception, lambda:template.render(c))
        del settings.UNIFORM_FAIL_SILENTLY

    def test_layout_fieldset_row_html_with_unicode_fieldnames(self):
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                Fieldset(
                    u'Company Data',
                    u'is_company',
                    css_id = "fieldset_company_data",
                    css_class = "fieldsets"
                ),
                Fieldset(
                    u'User Data',
                    u'email',
                    Row(
                        u'password1', 
                        u'password2',
                        css_id = "row_passwords",
                        css_class = "rows"
                    ),
                    HTML('<a href="#" id="testLink">test link</a>'),
                    u'first_name',
                    u'last_name',
                )
            )
        )

        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        c = Context({'form': TestForm(), 'form_helper': form_helper})
        html = template.render(c)

        self.assertTrue('id="fieldset_company_data"' in html)
        self.assertTrue('class="fieldsets' in html)
        self.assertTrue('id="row_passwords"' in html)
        self.assertTrue('class="rows"' in html)
        self.assertTrue('testLink' in html)

    def test_second_layout_multifield_column(self):
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                MultiField(
                    'is_company',
                    'email',
                    'password1', 
                    'password2',
                    css_id = "multifield_info",
                ),
                Column(
                    'first_name',
                    'last_name',
                    css_id = "column_name",
                )
            )
        )

        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        c = Context({'form': TestForm(), 'form_helper': form_helper})
        html = template.render(c)

        self.assertTrue('multiField' in html)
        self.assertTrue('formColumn' in html)
        self.assertTrue('id="multifield_info"' in html)
        self.assertTrue('id="column_name"' in html)

    def test_change_layout_dynamically_delete_field(self):
        template = get_template_from_string(u"""
            {% load uni_form_tags %}
            {% uni_form form form_helper %}
        """)        
        
        form = TestForm()
        form_helper = FormHelper()
        form_helper.add_layout(
            Layout(
                Fieldset(
                    u'Company Data',
                    'is_company',
                    'email',
                    'password1', 
                    'password2',
                    css_id = "multifield_info",
                ),
                Column(
                    'first_name',
                    'last_name',
                    css_id = "column_name",
                )
            )
        )

        # We remove email field on the go
        # Layout needs to be adapted for the new form fields
        del form.fields['email']
        del form_helper.layout.fields[0].fields[1]

        c = Context({'form': form, 'form_helper': form_helper})
        html = template.render(c)
        self.assertFalse('email' in html)
