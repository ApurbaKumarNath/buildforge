# users/models.py

#_________________________________________________________________________________________________________________________ (akn)

from django.db import models
# AbstractUser contains all the standard user fields: username, email, password, etc.
from django.contrib.auth.models import AbstractUser

# We are creating a new class that "extends" the built-in User model.
# This is the best way to add extra fields like bio and avatar to a user.
class CustomUser(AbstractUser):
    # We use a TextField for the bio because it can be longer than a standard CharField.
    # blank=True means the field is not required in forms.
    # null=True means the database can store a NULL value if no bio is provided.
    bio = models.TextField(blank=True, null=True)

    # ImageField is used for uploading files. 'avatars/' is the sub-folder within your MEDIA_ROOT
    # where these images will be saved.
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # By default, Django's User has is_staff and is_superuser fields.
    # We can use the is_staff field to represent our "Admin" role.
    # An Admin can create curated guides.
    # An EndUser is just a regular user (is_staff=False).
    # This perfectly implements our "User specialized into {Admin, EndUser}" logic.

    def __str__(self):
        # This is what will be displayed in the Django admin panel or when you print the object.
        return self.username
    
#_________________________________________________________________________________________________________________________