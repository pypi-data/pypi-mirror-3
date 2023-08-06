from django import forms

from crispy_forms.helpers import FormHelper, Fieldset, Field, Layout, Submit
from crispy_forms.bootstrap import FormActions

from . import models


class AchievementForm(forms.ModelForm):
    name = forms.CharField(label='Been good? <strong>The Sproutz</strong> lorem ipsum dolor sit amet. And then something else too.')
    target = forms.IntegerField(label='How many stars will you need?', min_value=models.TARGET_MIN, max_value=models.TARGET_MAX)
    next_url = forms.CharField(required=False, max_length=255, widget=forms.HiddenInput)

    class Meta:
        model = models.Achievement
        fields = ['name', 'target']

    helper = FormHelper()
    helper.form_tag = True
    helper.form_action = 'reward_create_goal'
    helper.form_class = 'add-goal-form'
    helper.layout = Layout(
        Fieldset(
            '',
            Field('name', placeholder='What is the goal?'),
            Field('target', placeholder='00', maxlength='2')
        ),
        FormActions(
            Submit('submit', 'Create', css_class='button')
        )
    )


class AchievementDeleteForm(forms.Form):
    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        FormActions(
            Submit('submit', 'Delete', css_class='button button-important')
        )
    )
