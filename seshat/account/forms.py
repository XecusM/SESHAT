from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
                                        AuthenticationForm,
                                        UserCreationForm,
                                        UserChangeForm,
                                        PasswordChangeForm,
                                        SetPasswordForm, )
from django.utils.translation import gettext_lazy as _

from seshat.images import crop_and_resize

from . import models


class MyAuthenticationForm(AuthenticationForm):
    '''
    Case-insensitive username login with a clear message for
    disabled accounts
    '''
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. "
            "Note password field is case-sensitive."
        ),
        'inactive': _('Your account is not active, please contact '
                      'the administrator for more details.'),
    }

    def clean(self):
        '''
        Authenticate the posted data
        '''
        username = (self.cleaned_data.get('username') or '').lower()
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                user = get_user_model().objects.filter(
                                                username=username).first()
                if user is not None and user.check_password(password):
                    self.confirm_login_allowed(user)
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class NewForm(UserCreationForm):
    '''
    Create New user
    '''
    class Meta:
        model = get_user_model()
        fields = [
                    'first_name', 'last_name', 'username',
                    'job', 'is_superuser', 'is_active'
            ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions for the new user form
        '''
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text = _("Enter user first name")
        self.fields['last_name'].help_text = _("Enter user last name")
        self.fields['username'].help_text = _("Enter a unique username")
        self.fields['job'].help_text = _("Enter user job title")
        self.fields['is_active'].initial = True
        if not self.user.is_superuser:
            del self.fields['is_superuser']

    def clean_username(self):
        '''
        Usernames are stored in lower case
        '''
        username = self.cleaned_data.get('username', '').lower()
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError(
                                _("This username already exists."),
                                code='username_used')
        return username


class EditForm(UserChangeForm):
    '''
    Edit User details
    '''
    password = None

    class Meta:
        model = get_user_model()
        fields = [
                    'first_name', 'last_name', 'username',
                    'job', 'is_superuser', 'is_active'
            ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions for the Edit user form
        '''
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text = _("Enter user first name")
        self.fields['last_name'].help_text = _("Enter user last name")
        self.fields['username'].help_text = _("Enter a unique username")
        self.fields['job'].help_text = _("Enter user job title")
        if not self.user.is_superuser:
            del self.fields['is_superuser']
        if self.instance == self.user:
            # nobody can disable their own account
            del self.fields['is_active']

    def clean_username(self):
        '''
        Usernames are stored in lower case
        '''
        username = self.cleaned_data.get('username', '').lower()
        if get_user_model().objects.filter(username=username).exclude(
                                        pk=self.instance.pk).exists():
            raise forms.ValidationError(
                                _("This username already exists."),
                                code='username_used')
        return username


class ProfileForm(forms.ModelForm):
    '''
    Form for user's profile
    '''
    class Meta:
        model = models.Profile
        fields = ['email', 'phone', 'birthdate', 'gender', ]

        widgets = {
            'birthdate': forms.DateInput(
                                    attrs={'type': 'date'},
                                    format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = _('Add your email')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")


class ProfilePhotoForm(forms.ModelForm):
    '''
    Form for the user profile photo with cropping
    '''
    #############################################################
    # Fields for image cropping
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    #############################################################

    class Meta:
        model = models.ProfilePhoto
        fields = ['photo', 'x', 'y', 'width', 'height', ]
        widgets = {
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['photo'].required = True
        self.fields['photo'].help_text = _(
                                    "Photo Recommended to be at least 200x200")

    def save(self, commit=True):
        '''
        Save the photo, cropped and resized to 200x200
        '''
        instance = super().save(commit=True)
        if instance.photo:
            crop_and_resize(
                        instance.photo.path,
                        self.cleaned_data.get('x'),
                        self.cleaned_data.get('y'),
                        self.cleaned_data.get('width'),
                        self.cleaned_data.get('height'),
                        size=200)
        return instance


class SettingsForm(forms.ModelForm):
    '''
    Form for user's settings
    '''
    class Meta:
        model = models.Settings
        fields = ['language', 'theme', 'paginate', 'default_page', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['language'].help_text = _("Select your interface language")
        self.fields['theme'].help_text = _(
                    "Select your interface theme (light, dark or automatic)")
        self.fields['paginate'].help_text = _("Number of items per page")
        self.fields['default_page'].help_text = _(
                                    "Select your favorite page after login")


class ChangePasswordForm(PasswordChangeForm):
    '''
    Change User Password
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = _('Current Password')
        self.fields['old_password'].widget.attrs['placeholder'] = _(
                                                        'Current password')
        self.fields['new_password1'].widget.attrs['placeholder'] = _(
                                                        'Enter new password')
        self.fields['new_password2'].widget.attrs['placeholder'] = _(
                                                        'Re-enter new password')


class ResetPasswordForm(SetPasswordForm):
    '''
    Administrator sets a new password for another user
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['placeholder'] = _(
                                                        'Enter new password')
        self.fields['new_password2'].widget.attrs['placeholder'] = _(
                                                        'Re-enter new password')
