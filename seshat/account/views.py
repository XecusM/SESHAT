from django.shortcuts import render
from django.views.generic import (
                                TemplateView, CreateView,
                                UpdateView, DetailView,
                                ListView, DeleteView, )
from django.contrib.auth.views import (
                                        PasswordChangeView,
                                        PasswordResetDoneView,
                                        PasswordResetView,
                                        LoginView, )
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils import translation
from django.contrib.auth.mixins import (
                                        LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin, )
from django.contrib.auth.decorators import (
                                        login_required,
                                        permission_required )
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import (
                                    activate,
                                    LANGUAGE_SESSION_KEY,
                                    ugettext_lazy as _)
from django.urls import translate_url
from django.contrib.auth.models import Permission

from x_django_app.views import XListView
from report.models import Activity
from report.views import RCreateView, RUpdateView, record_delete_object
from . import forms, models
from .functools import permissions, check_permisssions, get_url_link

# Create your views here.


class Index(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    '''
    View for account index page
    '''
    template_name = 'account/index.html'

    def test_func(self):
        '''
        Check if user ownership
        '''
        if self.request.user.has_perm('account.view_user'):
            return True
        if self.request.user.has_perm('account.backup'):
            return True
        if self.request.user.has_perm('account.restore'):
            return True
        if self.request.user.has_perm('account.export'):
            return True
        if self.request.user.has_perm('account.import'):
            return True
        if self.request.user.has_perm('report.view_activity'):
            return True

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['activity_list'] = Activity.objects.all(
                                                ).order_by('-created_at')[:10]
        return context


class Login(UserPassesTestMixin, LoginView):
    '''
    Class view for login
    '''
    # used template
    template_name = 'account/login.html'
    # raise 404 when fail
    raise_exception = True

    def test_func(self):
        '''
        Check if user is authenticated or not
        '''
        return not self.request.user.is_authenticated

    def post(self, request, *args, **kwargs):
        '''
        Method for posted data
        '''
        # assign variable for form data
        form = self.get_form()
        # Try to get the user details
        try:
            # assign user data to a variable
            user = get_user_model().objects.get(
                    username=self.request.POST.get('username'))
            # Check if the user is active
            if not user.is_active:
                # build a content for page details
                content = {
                    'error_message':
                        _('Your account is not active please contact \
                            adminstartor for more details.'), }
                # display content data
                return render(
                            request,
                            'account/login.html',
                            content)

        except Exception:
            # ignore if error occurs
            pass
        # check if form valid
        if form.is_valid():
            # get the valid method
            return self.form_valid(form)
        else:
            # get the invalid method
            return self.form_invalid(form)

    def get_success_url(self):
        '''
        Rediect url after login
        '''
        url = super(Login, self).get_success_url()
        user = self.request.user
        language = user.user_settings.language

        if url == reverse('index'):
            url = get_url_link(user, url)

        url = translate_url(url, language)
        activate(language)
        if hasattr(self.request, 'session'):
            self.request.session[LANGUAGE_SESSION_KEY] = language

        return url


class New(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Admin user can create a new account user
    '''
    permission_required = ('account.add_user',)
    template_name = 'account/new.html'
    model = get_user_model()
    form_class = forms.NewForm
    success_url = reverse_lazy('account:list')
    extra_context = {'permissions': permissions}

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        '''
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        self.object.save()

        for permission in permissions:
            for item in permission['permissions']:
                if item[0] in self.request.POST:
                    try:
                        user_permission = Permission.objects.get(
                                                        codename=item[0])
                        self.object.user_permissions.add(user_permission)
                    except Exception as error_type:
                        print(f"{item}-{error_type}")

        check_permisssions(self.object)

        self.object.refresh_from_db()

        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.CREATE,
                                user=self.request.user,
                                message=f"Account {self.object.username}"
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())


class List(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all account users
    '''
    permission_required = ('account.view_user',)
    template_name = 'account/list.html'
    model = get_user_model()
    search_fields = ['username', 'first_name', 'last_name']
    queryset = get_user_model().objects.all()
    ordering = ('username', 'first_name', 'last_name')

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class Details(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''
    View account user details
    '''
    template_name = 'account/details.html'
    model = get_user_model()
    queryset = get_user_model().objects.all()

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        return self.request.user == user \
                or self.request.user.has_perm('account.view_user')


class Edit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Edit account profile details
    '''
    permission_required = ('account.change_user',)
    template_name = 'account/edit.html'
    model = get_user_model()
    queryset = get_user_model().objects.all()
    form_class = forms.EditForm

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        '''
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        '''
        Valid form method
        '''
        self.object = form.save()
        self.object.save()

        for permission in permissions:
            for item in permission['permissions']:
                if item[0] in self.request.POST:
                    try:
                        user_permission = Permission.objects.get(
                                                            codename=item[0])
                        self.object.user_permissions.add(user_permission)
                    except Exception as error_type:
                        print(f"{item}-{error_type}")
                else:
                    try:
                        user_permission = Permission.objects.get(
                                                            codename=item[0])
                        if self.object.user_permissions.filter(
                                            id=user_permission.id).exists():
                            self.object.user_permissions.remove(
                                                    user_permission)
                    except Exception as error_type:
                        print(f"{item}-{error_type}")

        check_permisssions(self.object)

        self.object.refresh_from_db()

        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.EDIT,
                                user=self.request.user,
                                message=f"Account-{self.object.username}"
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *, object_list=None, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        # filter records with the given keywords
        if self.request.GET.get('next'):
            next = self.request.GET.get('next')
            kwargs.update({'next': next})
        context.update(kwargs)
        context['permissions'] = permissions
        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return reverse_lazy(
                                'account:details',
                                kwargs={'pk': self.object.id})


class ActivitiesList(LoginRequiredMixin, UserPassesTestMixin, XListView):
    '''
    View all staff activities
    '''
    template_name = 'account/activity.html'
    model = Activity
    ordering = ('-created_at')

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        return self.request.user == user \
                or self.request.user.has_perm('report.view_activity')

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, **kwargs):
        '''
        Send extra context to template
        '''
        context = super().get_context_data(**kwargs)
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        context['user'] = user
        return context

    def get_queryset(self):
        '''
        Get staff activities
        '''
        queryset = super().get_queryset()
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        queryset = queryset.filter(user=user)
        return queryset


class AllActivitiesList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    View all staff activities
    '''
    permission_required = ('report.view_activity',)
    template_name = 'account/all_activities.html'
    model = Activity
    search_fields = ['message', ]
    ordering = ('-created_at')

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class ProfileDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''
    View user profile details
    '''
    template_name = 'account/profile_details.html'
    model = models.UserProfile
    queryset = models.UserProfile.objects.all()

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(user_profile=self.kwargs['pk'])
        return self.request.user == user \
                or self.request.user.has_perm('account.view_user')


class EditProfile(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    RUpdateView):
    '''
    Edit an existing user profile view
    '''
    template_name = 'account/profile_edit.html'
    model = models.UserProfile
    form_class = forms.ProfileForm

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(user_profile=self.kwargs['pk'])
        return self.request.user == user

    def form_valid(self, form):
        '''
        Valid form method
        '''
        self.object = form.save()
        self.object.save()

        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.EDIT,
                                user=self.request.user,
                                message=f"Profile-{self.object.user.username}"
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy(
                            'account:profile_details',
                            kwargs={'pk': self.object.pk})


class SettingsDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''
    View user settings details
    '''
    template_name = 'account/settings_details.html'
    model = models.UserSettings
    queryset = models.UserSettings.objects.all()

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        return self.request.user == user


class EditSettings(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    RUpdateView):
    '''
    Edit an existing user settings view
    '''
    template_name = 'account/settings_edit.html'
    model = models.UserSettings
    form_class = forms.SettingsForm

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_user_model().objects.get(id=self.kwargs['pk'])
        return self.request.user == user

    def form_valid(self, form):
        '''
        Valid form method
        '''
        self.object = form.save()
        self.object.save()

        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.EDIT,
                                user=self.request.user,
                                message=f"Settings-{self.object.user.username}"
        )
        activity.save()

        translation.activate(self.object.language)
        self.request.session[
                        translation.LANGUAGE_SESSION_KEY
            ] = self.object.language
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        '''
        Method after success post
        '''
        return reverse_lazy(
                            'account:settings_details',
                            kwargs={'pk': self.object.pk})


class PasswordChange(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    PasswordChangeView):
    '''
    Class view for user change password
    '''
    # used template
    template_name = 'account/password_change.html'
    # View model
    model = get_user_model()
    # form class
    form_class = forms.ChangePasswordForm
    # success redirect url
    success_url = reverse_lazy('account:password_change_done')

    def test_func(self):
        '''
        Check if the requested user is the same as the user object
        '''
        user = get_user_model().objects.get(pk=self.kwargs['pk'])
        return self.request.user == user

    def get_success_url(self):
        '''
        Method after success post
        '''
        self.request.session['password_change'] = True
        return reverse_lazy('account:password_change_done')


class PasswordChangeDone(
                        LoginRequiredMixin,
                        UserPassesTestMixin,
                        TemplateView):
    '''
    Class view for confirms that password changed successfully
    '''
    # used template
    template_name = 'account/password_changed.html'

    def test_func(self):
        '''
        Check if the previous url page was change password url
        '''
        try:
            if self.request.session['password_change']:
                return True
            else:
                self.request.session['password_change'] = False
                return False
        except Exception:
            self.request.session['password_change'] = False
            return False

    def get(self, request, *args, **kwargs):
        '''
        add extra context to rendered template
        '''
        # go to user account details page
        context = {'next': reverse_lazy(
                                    'account:details',
                                    kwargs={'pk': self.request.user.id})}
        return self.render_to_response(context)


# Function Views


@login_required
@permission_required('account.delete_user', raise_exception=True)
def delete(request, pk):
    '''
    Delete user account
    '''
    if request.method == "POST":
        user = get_object_or_404(get_user_model(), pk=pk)
        # store user activity
        delete_object = record_delete_object(
                                        request,
                                        user,
                                        f"Account-{user.username}")
        if delete_object:
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('account:list')
        else:
            return render(request, 'news/error_message.html', {
                    'message': _("Couldn't delete the selected user"),
                    'link': reverse(
                                    'account:details',
                                    kwargs={'pk': user.pk})})
    else:
        raise Http404


@login_required
@permission_required('account.reset_password', raise_exception=True)
def reset_password(request, pk):
    '''
    Reset account user account password
    '''
    if request.method == 'POST':
        user = get_user_model().objects.get(pk=pk)
        if request.POST['password1'] and request.POST['password2'] \
                and request.POST['password1'] != request.POST['password2']:
            # give an error message if passwords not matches
            context = {
                    'error_message':
                    _('Password not matches or one of the passwords are blank')
            }
            return render(request, 'account/password_reset.html', context)
        else:
            user.set_password(request.POST['password1'])
            user.save()

            activity = Activity.objects.create_activity(
                                    activity_object=user,
                                    activity=Activity.RESET,
                                    user=request.user,
                                    message=f"Account {user.username}"
            )
            activity.save()

            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return HttpResponseRedirect(reverse_lazy(
                                                    'account:details',
                                                    kwargs={'pk': pk}))
    else:
        return render(request, 'account/password_reset.html')
