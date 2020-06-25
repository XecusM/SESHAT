from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# applicaton name
app_name = 'account'

 # patterns
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    # login pattern
    path('login/', views.Login.as_view(), name='login'),
    # logout pattern
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Add new user account
    path('new/', views.New.as_view(), name='new'),
    # view all accounts
    path('list/', views.List.as_view(), name='list'),
    # view user account details
    path(
        'details/<int:pk>/',
        views.Details.as_view(),
        name='details'
    ),
    # Edit user account
    path(
        'edit/<int:pk>/',
        views.Edit.as_view(),
        name='edit'
    ),
    # view user settings details
    path(
        'settings/<int:pk>/',
        views.SettingsDetails.as_view(),
        name='settings_details'
    ),
    # Edit user settings
    path(
        'settings/edit/<int:pk>/',
        views.EditSettings.as_view(),
        name='settings_edit'
    ),
    # view user profile details
    path(
        'profile/<int:pk>/',
        views.ProfileDetails.as_view(),
        name='profile_details'
    ),
    # Edit user profile
    path(
        'profile/edit/<int:pk>/',
        views.EditProfile.as_view(),
        name='profile_edit'
    ),
    # User activities list pattern
    path(
        'activity/<int:pk>/',
        views.ActivitiesList.as_view(),
        name='activities_list'
    ),
    # User activities list pattern
    path(
        'activities/',
        views.AllActivitiesList.as_view(),
        name='all_activities_list'
    ),
    # change password pattern
    path(
        'change-password/<int:pk>/',
        views.PasswordChange.as_view(),
        name='password_change'
    ),
    # change password done pattern
    path(
        'change-password-done/',
        views.PasswordChangeDone.as_view(),
        name='password_change_done'
    ),
    # delete user account
    path(
        'delete/<int:pk>/',
        views.delete,
        name='delete'
    ),
    # reset password for staff user
    path(
        'reset-password/<int:pk>/',
        views.reset_password,
        name='reset_password'
    ),
]
