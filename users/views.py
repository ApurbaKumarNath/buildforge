# users/views.py

#_________________________________________________________________________________________________________________________ (akn)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

# This is the view for the registration page.
def register(request):
    # The logic distinguishes between a user just arriving at the page (GET)
    # and a user who has submitted the form (POST).
    if request.method == 'POST':
        # If the form is submitted, we create a form instance and populate it with data from the request.
        form = CustomUserCreationForm(request.POST)
        # Django's form validation is powerful. It checks if the username already exists,
        # if passwords match (though that's handled by the form itself), etc.
        if form.is_valid():
            # If the form is valid, we save the user to the database.
            user = form.save()
            # After saving, we log the user in automatically.
            login(request, user)
            # Then, we redirect them to a 'home' page. We'll create this page next.
            return redirect('home')
    else:
        # If a user is just visiting the page, we create a blank instance of the form.
        form = CustomUserCreationForm()
    
    # We pass the form to the template in a dictionary called 'context'.
    context = {'form': form}
    # And render the HTML page, passing the context to it.
    return render(request, 'registration/register.html', context)

#_________________________________________________________________________________________________________________________