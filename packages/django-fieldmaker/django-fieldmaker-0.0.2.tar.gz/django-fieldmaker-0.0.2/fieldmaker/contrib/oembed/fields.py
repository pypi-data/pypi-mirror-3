from django import forms

from fieldmaker.fields import BaseField, BaseFieldForm
from fieldmaker.widgets import BaseWidget, BaseWidgetForm
from fieldmaker.resource import field_registry

class OembedFieldForm(BaseFieldForm):
    embed_code = forms.CharField()
    max_width = forms.IntegerField(min_value=0, required=False)
    max_height = forms.IntegerField(min_value=0, required=False)

class OembedField(BaseField):
    form = OembedFieldForm
    #field = recaptcha.RecaptchaField
    identities = ['OembedField']

field_registry.register_field('OembedField', OembedField)

