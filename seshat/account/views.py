from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (
                                        LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin, )
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse, translate_url
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import (
                                TemplateView, CreateView,
                                UpdateView, DetailView, )

from dateutil.relativedelta import relativedelta
from django_db_logger.models import StatusLog
from rest_framework.decorators import api_view
from rest_framework.response import Response
from x_django_app.models import XActivity
from x_django_app.views import XListView, XUpdateView, x_record_delete_object

from seshat.functools import get_next_url, NextUrlMixin as BaseNextUrlMixin

from . import forms, models, report_data
from .functools import (
                        permissions, set_permissions,
                        get_user_permission_names, get_url_link, )


# Help functions


class NextUrlMixin(BaseNextUrlMixin):
    '''
    Account pages go back to the user details page
    '''

    def get_default_success_url(self):
        '''
        The url used when no "next" url is sent
        '''
        return reverse('account:UserDetails', kwargs={'pk': self.object.user.id})


def can_view_user(request_user, user):
    '''
    A user can always see themselves; others need the view permission
    '''
    return request_user == user or request_user.has_perm('account.view_user')


def can_view_report(request_user, user):
    '''
    A user can see their own report; others need report + view permissions
    '''
    return request_user == user or (
                    request_user.has_perm('account.report_activity')
                    and request_user.has_perm('account.view_user'))


# Create your views here.


class Index(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    '''
    View for administration dashboard page
    '''
    template_name = 'account/index.html'
    dashboard_permissions = (
                            'account.view_user', 'account.backup',
                            'account.restore', 'account.export',
                            'account.import', 'account.view_activity',
                            'django_db_logger.view_statuslog', )

    def test_func(self):
        '''
        Any administration permission gives access to the dashboard
        '''
        return any(self.request.user.has_perm(permission)
                   for permission in self.dashboard_permissions)

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.has_perm('account.view_activity'):
            context['activity_list'] = XActivity.objects.select_related(
                                        'user').order_by('-created_at')[:10]
            context['activities_count'] = XActivity.objects.filter(
                                created_at__date__gte=timezone.localdate(
                                    ) - relativedelta(days=30)).count()

        if user.has_perm('account.view_user'):
            context['active_users_count'] = get_user_model().objects.filter(
                                                    is_active=True).count()
            context['users_count'] = get_user_model().objects.count()

        if user.has_perm('django_db_logger.view_statuslog'):
            context['errors_count'] = StatusLog.objects.filter(
                                                    level__gte=40).count()

        return context


class Login(UserPassesTestMixin, LoginView):
    '''
    Class view for login
    '''
    template_name = 'account/login.html'
    form_class = forms.MyAuthenticationForm

    def test_func(self):
        '''
        Only anonymous users can open the login page
        '''
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        '''
        Signed-in users are sent to their default page
        '''
        return redirect(get_url_link(self.request.user))

    def get_success_url(self):
        '''
        Redirect url after login: the next url or the user's default page,
        in the user's language
        '''
        user = self.request.user
        language = user.user_settings.language

        url = get_next_url(self.request, '') or get_url_link(user)
        return translate_url(url, language)

    def form_valid(self, form):
        '''
        Remember the user's language in the language cookie
        '''
        response = super().form_valid(form)
        response.set_cookie(
                        'django_language',
                        self.request.user.user_settings.language)
        return response


class NewUser(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Admin user can create a new account user
    '''
    permission_required = ('account.add_user',)
    template_name = 'account/user_new.html'
    model = get_user_model()
    form_class = forms.NewForm

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        '''
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        '''
        Send the permissions list to the template
        '''
        context = super().get_context_data(**kwargs)
        context['permissions'] = permissions
        context['user_permissions'] = set(self.request.POST.getlist(
                                                            'permissions'))
        return context

    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        set_permissions(self.object, self.request.POST.getlist('permissions'))

        XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=XActivity.CREATE,
                                user=self.request.user,
                                message=f"Account-{self.object.username}"
        )
        messages.success(self.request, _('The account has been created'))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        '''
        Method after success post
        '''
        return get_next_url(
                        self.request,
                        reverse('account:UserDetails',
                                kwargs={'pk': self.object.id}))


class UsersList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all account users
    '''
    permission_required = ('account.view_user',)
    template_name = 'account/users_list.html'
    model = get_user_model()
    search_fields = ['username', 'first_name', 'last_name', 'job']
    queryset = get_user_model().objects.all()
    ordering = ('username', 'first_name', 'last_name')
    context_object_name = 'users_list'

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class UserDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''
    View account user details
    '''
    template_name = 'account/user_details.html'
    model = get_user_model()
    queryset = get_user_model().objects.all()
    context_object_name = 'account'

    def test_func(self):
        '''
        Check if user ownership
        '''
        user = get_object_or_404(get_user_model(), pk=self.kwargs['pk'])
        return can_view_user(self.request.user, user)


class EditUser(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Edit account user details
    '''
    permission_required = ('account.change_user',)
    template_name = 'account/user_edit.html'
    model = get_user_model()
    queryset = get_user_model().objects.all()
    form_class = forms.EditForm
    context_object_name = 'account'

    def has_permission(self):
        '''
        Only administrators can edit administrators
        '''
        user = get_object_or_404(get_user_model(), pk=self.kwargs['pk'])
        if user.is_superuser and not self.request.user.is_superuser:
            return False
        return super().has_permission()

    def get_form_kwargs(self):
        '''
        Return the keyword arguments for instantiating the form.
        '''
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        '''
        Valid form method
        '''
        self.object = form.save()

        XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=XActivity.EDIT,
                                user=self.request.user,
                                message=f"Account-{self.object.username}"
        )
        messages.success(self.request, _('The account has been updated'))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['next'] = get_next_url(self.request, '')
        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        return get_next_url(
                        self.request,
                        reverse('account:UserDetails',
                                kwargs={'pk': self.object.id}))


class EditPermission(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Edit user permissions
    '''
    permission_required = ('account.change_user',)
    template_name = 'account/permission_edit.html'

    def get_object(self):
        '''
        Get the selected user
        '''
        return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        """
        Save the selected permissions
        """
        self.object = self.get_object()
        set_permissions(self.object, request.POST.getlist('permissions'))

        XActivity.objects.create_activity(
                                activity_object=self.object,
                                activity=XActivity.EDIT,
                                user=self.request.user,
                                message=f"Permissions-{self.object.username}"
        )
        messages.success(request, _('Permissions have been updated'))

        return HttpResponseRedirect(get_next_url(
                        request,
                        reverse('account:DetailedPermission',
                                kwargs={'pk': self.object.id})))

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        account = self.get_object()
        context['account'] = account
        context['permissions'] = permissions
        context['user_permissions'] = get_user_permission_names(account)
        context['next'] = get_next_url(self.request, '')
        return context


class DetailedPermission(
                        LoginRequiredMixin,
                        PermissionRequiredMixin,
                        TemplateView):
    '''
    View user permissions
    '''
    permission_required = ('account.view_user',)
    template_name = 'account/permission_details.html'

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        account = get_object_or_404(get_user_model(), pk=self.kwargs['pk'])
        context['account'] = account
        context['permissions'] = permissions
        context['user_permissions'] = get_user_permission_names(account)
        return context


class EditProfile(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    NextUrlMixin,
                    XUpdateView):
    '''
    Edit an existing user profile view
    '''
    template_name = 'account/profile_edit.html'
    model = models.Profile
    form_class = forms.ProfileForm

    def test_func(self):
        '''
        Only the owner can edit the profile
        '''
        profile = get_object_or_404(models.Profile, pk=self.kwargs['pk'])
        return self.request.user == profile.user

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Profile-{object.user.username}"


class EditSettings(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    NextUrlMixin,
                    XUpdateView):
    '''
    Edit an existing user settings view
    '''
    template_name = 'account/settings_edit.html'
    model = models.Settings
    form_class = forms.SettingsForm

    def test_func(self):
        '''
        Only the owner can edit the settings
        '''
        user_settings = get_object_or_404(models.Settings, pk=self.kwargs['pk'])
        return self.request.user == user_settings.user

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Settings-{object.user.username}"

    def form_valid(self, form):
        '''
        Switch to the selected language
        '''
        response = super().form_valid(form)
        language = self.object.language
        response = HttpResponseRedirect(
                        translate_url(self.get_success_url(), language))
        response.set_cookie('django_language', language)
        return response


class PhotoEdit(LoginRequiredMixin, UserPassesTestMixin, NextUrlMixin, XUpdateView):
    '''
    Class view for edit user photo
    '''
    template_name = 'account/photo_edit.html'
    model = models.ProfilePhoto
    form_class = forms.ProfilePhotoForm
    queryset = models.ProfilePhoto.objects.all()

    def test_func(self):
        '''
        Check photo ownership
        '''
        photo = get_object_or_404(models.ProfilePhoto, pk=self.kwargs['pk'])
        return self.request.user == photo.user

    def get_message(self, object):
        '''
        return activity message for the selected object
        '''
        return f"Photo-{object.user.username}"


class UserActivities(LoginRequiredMixin, UserPassesTestMixin, XListView):
    '''
    View all activities of a user
    '''
    template_name = 'account/user_activities.html'
    model = XActivity
    search_fields = ['message', ]
    ordering = ('-created_at', )

    def get_account(self):
        '''
        Get the selected user
        '''
        return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

    def test_func(self):
        '''
        Check if user ownership
        '''
        return self.request.user == self.get_account() \
            or self.request.user.has_perm('account.view_activity')

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
        context['account'] = self.get_account()
        return context

    def get_queryset(self):
        '''
        Get user activities
        '''
        return super().get_queryset().filter(user=self.get_account())


class ActivitiesList(
                        LoginRequiredMixin,
                        PermissionRequiredMixin,
                        XListView):
    '''
    View all users' activities
    '''
    permission_required = ('account.view_activity',)
    template_name = 'account/activities_list.html'
    model = XActivity
    search_fields = ['message', 'user__username', ]
    ordering = ('-created_at', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['from_date'] = self.request.GET.get('from_date', '')
        context['to_date'] = self.request.GET.get('to_date', '')
        context['activity'] = self.request.GET.get('activity', '')
        context['activity_choices'] = XActivity.activity_choices
        return context

    def get_queryset(self):
        '''
        Filter by date range and activity type
        '''
        queryset = super().get_queryset().select_related('user')
        if self.request.GET.get('from_date'):
            queryset = queryset.filter(
                        created_at__date__gte=self.request.GET.get('from_date'))
        if self.request.GET.get('to_date'):
            queryset = queryset.filter(
                        created_at__date__lte=self.request.GET.get('to_date'))
        if self.request.GET.get('activity'):
            queryset = queryset.filter(
                        activity=self.request.GET.get('activity'))
        return queryset


class PasswordChange(
                    LoginRequiredMixin,
                    UserPassesTestMixin,
                    PasswordChangeView):
    '''
    Class view for user change password
    '''
    template_name = 'account/password_change.html'
    form_class = forms.ChangePasswordForm
    success_url = reverse_lazy('account:PasswordChangeDone')

    def test_func(self):
        '''
        Check if the requested user is the same as the user object
        '''
        return self.request.user.pk == self.kwargs['pk']

    def form_valid(self, form):
        '''
        Mark the password change for the done page
        '''
        self.request.session['password_change'] = True
        return super().form_valid(form)


class PasswordChangeDone(
                        LoginRequiredMixin,
                        UserPassesTestMixin,
                        TemplateView):
    '''
    Class view for confirms that password changed successfully
    '''
    template_name = 'account/password_changed.html'

    def test_func(self):
        '''
        Check if the previous page was the change password page
        '''
        return bool(self.request.session.pop('password_change', False))


class LogEntryList(LoginRequiredMixin, PermissionRequiredMixin, XListView):
    '''
    List of all log entries
    '''
    permission_required = ('django_db_logger.view_statuslog',)
    template_name = 'account/logs_list.html'
    model = StatusLog
    search_fields = ['logger_name', 'msg', ]
    queryset = StatusLog.objects.all()
    ordering = ('-create_datetime', )

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        return self.request.user.user_settings.paginate


class DetailedLogEntry(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    View log entry details
    '''
    permission_required = ('django_db_logger.view_statuslog',)
    template_name = 'account/log_details.html'
    model = StatusLog
    queryset = StatusLog.objects.all()


class UserReport(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    '''
    Personal activity report for a single user: viewable by the user
    themselves, or by anyone with both the report and view permissions
    '''
    template_name = 'account/user_report.html'

    def test_func(self):
        '''
        Check user ownership or the report+view permissions
        '''
        user = get_object_or_404(get_user_model(), pk=self.kwargs['pk'])
        return can_view_report(self.request.user, user)

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        context['account'] = get_object_or_404(
                                        get_user_model(), pk=self.kwargs['pk'])
        to_date = timezone.localdate()
        context['default_from_date'] = to_date.replace(
                                            day=1) - relativedelta(months=11)
        context['default_to_date'] = to_date
        return context


class ActivitiesReport(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    '''
    Organization activity report, scoped to active users
    '''
    permission_required = ('account.report_activity', 'account.view_user')
    template_name = 'account/activities_report.html'

    def get_context_data(self, **kwargs):
        '''
        Get the context for this view.
        '''
        context = super().get_context_data(**kwargs)
        to_date = timezone.localdate()
        context['default_from_date'] = to_date.replace(
                                            day=1) - relativedelta(months=11)
        context['default_to_date'] = to_date
        return context


# Function Views


@login_required
@permission_required('account.delete_user', raise_exception=True)
@require_POST
def delete_user(request, pk):
    '''
    Delete user account
    '''
    user = get_object_or_404(get_user_model(), pk=pk)
    if user == request.user or (
                        user.is_superuser and not request.user.is_superuser):
        return render(request, 'error_message.html', {
                'message': _("You can't delete the selected account"),
                'link': reverse('account:UserDetails', kwargs={'pk': user.pk})})

    if x_record_delete_object(request, user, f"Account-{user.username}"):
        messages.success(request, _('The account has been deleted'))
        return redirect(get_next_url(request, reverse('account:UsersList')))

    return render(request, 'error_message.html', {
            'message': _("Couldn't delete the selected account, it is "
                         "linked to other records. Disable it instead."),
            'link': reverse('account:UserDetails', kwargs={'pk': user.pk})})


@login_required
@require_POST
def photo_remove(request, pk):
    '''
    Delete profile photo
    '''
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.user != user:
        return render(request, 'error/403.html', status=403)

    user.user_photo.photo.delete()
    return redirect(get_next_url(
                    request,
                    reverse('account:UserDetails', kwargs={'pk': user.id})))


@login_required
@require_POST
def toggle_theme(request):
    '''
    Switch the user's theme between light and dark
    '''
    user_settings = request.user.user_settings
    if user_settings.theme == models.Settings.DARK:
        user_settings.theme = models.Settings.LIGHT
    elif user_settings.theme == models.Settings.LIGHT:
        user_settings.theme = models.Settings.DARK
    else:
        # automatic theme: switch to the opposite of what the browser shows
        if request.POST.get('current') == 'dark':
            user_settings.theme = models.Settings.LIGHT
        else:
            user_settings.theme = models.Settings.DARK
    user_settings.save()
    return redirect(get_next_url(request, reverse('Index')))


@login_required
@permission_required('account.reset_password', raise_exception=True)
def reset_password(request, pk):
    '''
    Reset another user account password
    '''
    user = get_object_or_404(get_user_model(), pk=pk)
    if user.is_superuser and not request.user.is_superuser:
        return render(request, 'error/403.html', status=403)

    form = forms.ResetPasswordForm(user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if user == request.user:
            update_session_auth_hash(request, user)

        XActivity.objects.create_activity(
                                activity_object=user,
                                activity=XActivity.RESET,
                                user=request.user,
                                message=f"Account-{user.username}"
        )
        messages.success(request, _('The password has been reset'))
        return redirect(get_next_url(
                    request,
                    reverse('account:UserDetails', kwargs={'pk': pk})))

    return render(
            request,
            'account/password_reset.html',
            {'account': user, 'form': form})


# Report APIs


@api_view(['GET'])
def report_user_activity(request, pk):
    '''
    Personal activity report data for a single user
    '''
    user = get_object_or_404(get_user_model(), pk=pk)

    if not can_view_report(request.user, user):
        return Response(status=403)

    return Response(report_data.build_user_report(user, request))


@api_view(['GET'])
def report_all_activities(request):
    '''
    Organization activity report data, scoped to active users
    '''
    if not (request.user.has_perm('account.report_activity')
            and request.user.has_perm('account.view_user')):
        return Response(status=403)

    return Response(report_data.build_all_users_report(request))

