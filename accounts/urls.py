# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.CreateUserView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('test-token/', views.TestTokenView.as_view(), name='test-token'),
    path('list-users/', views.ListUsersView.as_view(), name='list-users'),
    path('activate/<str:user_id>/', views.ActivateUserView.as_view(), name='activate-account'),
    path('deactivate/<str:user_id>/', views.DesactivateUserView.as_view(), name='deactivate-account'),
    path('user/<str:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    path('edit-user-admin/<str:user_id>/', views.UserEditAdminView.as_view(), name='edit-user-admin'),
    path('edit-user/', views.UserEditView.as_view(), name='edit-user'),
]