from django.shortcuts import render
from django.views.generic import (TemplateView, CreateView, UpdateView, )
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import transaction

from .models import Activity

# Create your views here.


class RCreateView(CreateView):
    '''
    Create a new object with activity and created_by for requested user
    '''

    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        self.object.created_by = self.request.user
        self.object.save()
        # Store user activity
        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.CREATE,
                                user=self.request.user,
                                message=self.get_message(self.object)
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"


class RUpdateView(UpdateView):
    '''
    Edit an existing object with activity and edited for requested user
    '''
    def form_valid(self, form):
        '''
        Method for valid form
        '''
        self.object = form.save()
        self.object.edited(self.request.user)
        self.object.save()
        self.object.refresh_from_db()
        # Store user activity
        activity = Activity.objects.create_activity(
                                activity_object=self.object,
                                activity=Activity.EDIT,
                                user=self.request.user,
                                message=self.get_message(self.object)
        )
        activity.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_message(self, object):
        '''
        return activity messsage for the selected object
        '''
        return f"Object-{object.id}"


# Help Functions


def record_delete_object(request, object, message):
    '''
    Record delete activity to requested user
    '''
    activity = Activity.objects.create_activity(
                        activity_object=object,
                        activity=Activity.DELETE,
                        user=request.user,
                        message=message
    )
    activity.save()

    try:
        with transaction.atomic():
            object.delete()
    except Exception as error_type:
        activity.delete()
        return False
    return True
