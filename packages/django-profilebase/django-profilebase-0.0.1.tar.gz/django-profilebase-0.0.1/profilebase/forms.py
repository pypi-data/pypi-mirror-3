from django import forms
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _


class NewPasswordForm(forms.Form):
    password = forms.CharField(
        label=_(u'Password'),
        min_length=4,
        max_length=100,
        widget=forms.PasswordInput(),
        )
    confirm_password = forms.CharField(
        label=_(u'Confirm password'),
        min_length=4,
        max_length=100,
        widget=forms.PasswordInput(),
        )

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError(_(u'Password do not match'))
        return self.cleaned_data


class LoginForm(forms.Form):
    login = forms.CharField(
        label=_('Login'),
        min_length=1,
        max_length=500
        )
    password = forms.CharField(
        label=_('Password'),
        min_length=4,
        max_length=100,
        widget=forms.PasswordInput()
        )

    def __init__(self, authenticate, **kwargs):
        self.authenticate = authenticate
        self.request = kwargs.pop('request')
        self.profile = None
        super(LoginForm, self).__init__(**kwargs)

    def clean(self):
        login = self.cleaned_data.get('login')
        password = self.cleaned_data.get('password')
        if login and password:
            self.profile = self.authenticate(login, password)
            if self.profile is None:
                raise ValidationError(_("Wrong login or password."))
            elif not self.profile.is_active:
                raise ValidationError(_("This account is inactive."))
        if self.request and not self.request.session.test_cookie_worked():
            raise ValidationError(
                _("Your Web browser doesn't appear to have cookies enabled. "
                  "Cookies are required for logging in.")
                )
        return self.cleaned_data

