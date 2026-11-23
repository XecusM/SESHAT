'''
Helpers shared by the views of all applications
'''
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _

from x_django_app.views import x_record_delete_object


def get_next_url(request, default):
    '''
    Return the safe "next" url from the request, or the default one
    '''
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
                                    next_url,
                                    allowed_hosts={request.get_host()},
                                    require_https=request.is_secure()):
        return next_url
    return default


class PaginateMixin:
    '''
    Use the page limit from the user's settings
    '''

    def get_paginate_by(self, queryset):
        '''
        return paginate_by number
        '''
        try:
            return self.request.user.user_settings.paginate
        except Exception:
            return 30


class NextUrlMixin:
    '''
    Send the "next" url to the template and redirect to it after a
    successful post. Views define get_default_success_url().
    '''

    def get_context_data(self, **kwargs):
        '''
        Send the next url to the template
        '''
        context = super().get_context_data(**kwargs)
        context['next'] = get_next_url(self.request, '')
        return context

    def get_success_url(self):
        '''
        Method after success post
        '''
        return get_next_url(self.request, self.get_default_success_url())

    def get_default_success_url(self):
        '''
        The url used when no "next" url is sent
        '''
        return self.object.get_absolute_url()


def delete_object(request, model, pk, message, success_url, error_link=None):
    '''
    Delete an object recording the user activity, or render the error page
    when it is linked to other records
    '''
    instance = get_object_or_404(model, pk=pk)
    can_be_deleted = getattr(instance, 'can_be_deleted', None)
    if (can_be_deleted is None or can_be_deleted()) and \
            x_record_delete_object(request, instance, message(instance)):
        messages.success(
                    request,
                    _('%(name)s has been deleted') % {'name': instance})
        return redirect(get_next_url(request, success_url))

    return render(request, 'error_message.html', {
        'message': _("Couldn't delete %(name)s, it is linked to other "
                     "records.") % {'name': instance},
        'link': error_link or success_url,
    })
