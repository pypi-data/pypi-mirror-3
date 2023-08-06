from django import forms
from ccstraps.models import Strap


class StrapAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StrapAdminForm, self).__init__(*args, **kwargs)
        self.fields['name'].help_text = 'Use only lowercase alphanumerics'
        self.fields['delay'].help_text = 'In milliseconds'

    class Meta:
        model = Strap

    class Media:
        css = {
            'screen': ('ccstraps/css/admin.css',)
        }

    def clean_delay(self):
        if self.cleaned_data['delay'] < 1000:
            raise forms.ValidationError('Minimum delay is 1000')
        return self.cleaned_data['delay']
