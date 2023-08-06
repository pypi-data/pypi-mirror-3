from django import forms


class MetadataForm(forms.Form):
    page_id = forms.CharField(required=False)
    title = forms.CharField(required=False)
    description = forms.CharField(required=False)
    image = forms.CharField(required=False)
    keywords = forms.CharField(required=False)
    author = forms.CharField(required=False)
