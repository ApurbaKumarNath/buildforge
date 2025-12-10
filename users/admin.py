# users/admin.py

#__________________________________________________________________________________________________________________________ (akn)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# We are telling the admin panel to use the default UserAdmin interface
# but for our CustomUser model. This gives us all the nice user management features.
admin.site.register(CustomUser, UserAdmin)

#__________________________________________________________________________________________________________________________