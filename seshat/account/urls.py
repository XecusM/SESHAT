from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

# application name
app_name = 'account'

# patterns
urlpatterns = [
    # administration dashboard
    path('', views.Index.as_view(), name='Index'),
    # login pattern
    path('login/', views.Login.as_view(), name='Login'),
    # logout pattern (POST only)
    path('logout/', auth_views.LogoutView.as_view(), name='Logout'),
    # switch between light and dark theme
    path('theme/', views.toggle_theme, name='ToggleTheme'),
    # Add new user account
    path('new/', views.NewUser.as_view(), name='NewUser'),
    # view all accounts
    path('list/', views.UsersList.as_view(), name='UsersList'),
    # view user account details
    path('details/<int:pk>/', views.UserDetails.as_view(), name='UserDetails'),
    # Edit user account
    path('edit/<int:pk>/', views.EditUser.as_view(), name='EditUser'),
    # Edit user permissions
    path(
        'permissions/edit/<int:pk>/',
        views.EditPermission.as_view(),
        name='EditPermission'),
    # view user permissions
    path(
        'permissions/<int:pk>/',
        views.DetailedPermission.as_view(),
        name='DetailedPermission'),
    # Edit user settings
    path(
        'settings/edit/<int:pk>/',
        views.EditSettings.as_view(),
        name='EditSettings'),
    # Edit user profile
    path(
        'profile/edit/<int:pk>/',
        views.EditProfile.as_view(),
        name='EditProfile'),
    # Edit profile photo pattern
    path('photo/edit/<int:pk>/', views.PhotoEdit.as_view(), name='PhotoEdit'),
    # remove profile photo pattern
    path('photo/remove/<int:pk>/', views.photo_remove, name='PhotoRemove'),
    # User activities list pattern
    path(
        'activity/<int:pk>/',
        views.UserActivities.as_view(),
        name='UserActivities'),
    # User activity report pattern
    path('report/<int:pk>/', views.UserReport.as_view(), name='UserReport'),
    # All activities list pattern
    path(
        'activities/',
        views.ActivitiesList.as_view(),
        name='ActivitiesList'),
    # All users' activity report pattern
    path(
        'activities/report/',
        views.ActivitiesReport.as_view(),
        name='ActivitiesReport'),
    # user activity report data
    path(
        'api/report/user/<int:pk>/',
        views.report_user_activity,
        name='APIReportUser'),
    # all users' activity report data
    path(
        'api/report/activities/',
        views.report_all_activities,
        name='APIReportActivities'),
    # change password pattern
    path(
        'change-password/<int:pk>/',
        views.PasswordChange.as_view(),
        name='PasswordChange'),
    # change password done pattern
    path(
        'change-password-done/',
        views.PasswordChangeDone.as_view(),
        name='PasswordChangeDone'),
    # delete user account
    path('delete/<int:pk>/', views.delete_user, name='DeleteUser'),
    # reset password for another user
    path(
        'reset-password/<int:pk>/',
        views.reset_password,
        name='PasswordReset'),
    # List of all log entries
    path('logs/', views.LogEntryList.as_view(), name='LogEntryList'),
    # log entry details
    path('log/<int:pk>/', views.DetailedLogEntry.as_view(), name='DetailedLogEntry'),
]
