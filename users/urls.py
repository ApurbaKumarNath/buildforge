# users/urls.py

#_________________________________________________________________________________________________________________________ (akn)

from django.urls import path
# Import Django's built-in views for login and logout
from django.contrib.auth import views as auth_views
from . import views # Import our own views.py

app_name = 'users'

urlpatterns = [
    # Our custom registration view
    path('register/', views.register, name='register'),

    # Django's built-in Login view. We just need to tell it which template to use.
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Django's built-in Logout view. It doesn't even need a template.
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile, name='profile'),
]

#_________________________________________________________________________________________________________________________ (akn)