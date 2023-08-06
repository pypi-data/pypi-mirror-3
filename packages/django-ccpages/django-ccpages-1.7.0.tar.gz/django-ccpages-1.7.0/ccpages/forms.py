import hashlib
from django import forms
from mptt.forms import TreeNodeChoiceField
from mptt.admin import MPTTAdminForm
from writingfield import FullScreenTextarea
from ccpages.models import Page


class PageAdminForm(MPTTAdminForm):

    class Meta:
        model = Page
        widgets = {
            'content': FullScreenTextarea()
        }
    class Media:
        css = {
                'screen': ('ccpages/css/admin.css',)
            }

class PagePasswordForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page', None)
        super(PagePasswordForm, self).__init__(*args, **kwargs)


    def clean_password(self):
        page_hash = self.page.hash
        password = self.cleaned_data['password']
        user_hash = hashlib.sha1(password).hexdigest()
        if user_hash == page_hash:
            self.hash = user_hash
            return password
        raise forms.ValidationError('Incorrect password')
