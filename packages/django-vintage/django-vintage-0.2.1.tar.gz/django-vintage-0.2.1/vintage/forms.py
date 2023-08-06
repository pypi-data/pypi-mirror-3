from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import ArchivedPage


class ArchivedpageForm(forms.ModelForm):
    url = forms.RegexField(
        label=_("URL"),
        max_length=100,
        regex=r'^[-\w/\.~]+$',
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                    " slashes."),
        error_message=_("This value must contain only letters, numbers,"
                        " dots, underscores, dashes, slashes or tildes."))

    class Meta:
        model = ArchivedPage

    def clean_url(self):
        url = self.cleaned_data['url']
        if not url.startswith('/'):
            raise forms.ValidationError(ugettext("URL is missing a leading slash."))
        return url

    def clean(self):
        url = self.cleaned_data.get('url', None)

        same_url = ArchivedPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if same_url.count():
            raise forms.ValidationError(
                _('An archived page with url %(url)s already exists.' %
                  {'url': url, }))

        return super(ArchivedpageForm, self).clean()
