import hashlib
from django import forms
from ccpages.models import Page


class PageAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)
        # TODO: is there a better way to prevent the TreeNodeChoiceField
        # form widget displaying invalid moves?
        if self.instance.pk is not None:
            self.fields['parent'].queryset = self.fields['parent'].queryset\
                    .exclude(
                            pk__in=[self.instance.pk]
                    ).exclude(
                            pk__in=[d.pk for d in self.instance.get_children()]
                    )

    class Meta:
        model = Page

    class Media:
        css = {
                'screen': ('ccpages/admin.css',)
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
