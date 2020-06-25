from django import forms
from PIL import Image
from django.contrib.auth.forms import (
                                        UserCreationForm,
                                        UserChangeForm,
                                        PasswordChangeForm,
                                        PasswordResetForm, )
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _

from . import models


class NewForm(UserCreationForm):
    '''
    Create New user
    '''
    # error messages for email and password matches
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'email_used': _("This email already exists."),
        'username_used': _("This username already exists."),
    }
    class Meta:
        model = get_user_model()
        fields = [
                    'first_name', 'last_name', 'username',
                    'password1', 'password2',
                    'job', 'is_superuser', 'is_active'
            ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions for the SignUp form class
        '''
        self.user = kwargs.pop('user')
        # get the initial form class values
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text = _("Enter user first name")
        self.fields['last_name'].help_text = _("Enter user last name")
        self.fields['username'].help_text = _("Enter a unique username")
        self.fields['job'].help_text = _("Enter user job title")
        # initate is_active
        self.fields['is_active'].initial = True
        if not self.user.is_superuser:
            del self.fields['is_superuser']


class EditForm(UserChangeForm):
    '''
    Edit User details
    '''
    # error messages for email and password matches
    error_messages = {
        'email_used': _("This email already exists."),
        'username_used': _("This username already exists."),
    }
    password = None
    class Meta:
        model = get_user_model()
        fields = [
                    'first_name', 'last_name', 'username',
                    'job', 'is_superuser', 'is_active'
            ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions for the Edit user form class
        '''
        self.user = kwargs.pop('user')
        # get the initial form class values
        super().__init__(*args, **kwargs)
        self.fields['first_name'].help_text = _("Enter user first name")
        self.fields['last_name'].help_text = _("Enter user last name")
        self.fields['username'].help_text = _("Enter a unique username")
        self.fields['job'].help_text = _("Enter user job title")
        if not self.user.has_perm('account.change_user'):
            self.fields['username'].widget.attrs['disabled'] = True
            del self.fields['is_active']
        if not self.user.is_superuser:
            del self.fields['is_superuser']


class ProfileForm(forms.ModelForm):
    '''
    Form for user's profile
    '''
    #############################################################
    # Fields for image cropping
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    #############################################################

    class Meta:
        model = models.UserProfile
        fields = ['photo', 'email', 'phone', 'birthdate', 'gender', ]

        widgets = {
            'birthdate': forms.TextInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['photo'].help_text = _(
                                    "Profile photo must be at least 200x200")
        self.fields['email'].widget.attrs['placeholder'] = _('Add your email')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")

    def save(self, commit=True):
        '''
        save for with cropped image
        '''
        form = super().save(commit=True)
        # check if image sent
        if form.photo:
            try:
                # get cropping data
                x = self.cleaned_data.get('x')
                y = self.cleaned_data.get('y')
                w = self.cleaned_data.get('width')
                h = self.cleaned_data.get('height')

                # get the save image path
                image = Image.open(form.photo.path)
                cropped_image = image.crop((x, y, w + x, h + y))
                # check if image size more than 200kb
                if cropped_image.size[0] * cropped_image.size[1] < \
                        0.2 * 1024 * 1024:
                    raise forms.ValidationError(
                                    _('Image file too small ( < 200kb )'))
                else:
                    # resize the image after cropping
                    resized_image = cropped_image.resize(
                                                    (200, 200),
                                                    Image.ANTIALIAS)
                    resized_image.save(form.photo.path)
                    return form
            except Exception as error_type:
                print(error_type)
                return form
        else:
            form.save()
            return form


class SettingsForm(forms.ModelForm):
    '''
    Form for user's settings
    '''
    class Meta:
        model = models.UserSettings
        fields = ['language', 'paginate', 'default_page', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['language'].help_text = _("Select you interface language")
        self.fields['paginate'].help_text = _("Number of items per page")
        self.fields['default_page'].help_text = _(
                                    "Select you favorite page after login")


class ChangePasswordForm(PasswordChangeForm):
    '''
    Change User Password
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label =( _('Current Password'))
        self.fields['old_password'].help_text = _("Enter your old password")
        self.fields['new_password2'].help_text = _(
                                                "Enter the same new password")
