# users/views.py

#_________________________________________________________________________________________________________________________ (akn)
from .forms import PasswordToggleWidget
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from .models import CustomUser


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

def profile(request, username):
    from marketplace.models import MarketplaceListing
    user = get_object_or_404(CustomUser, username=username)
    listings = MarketplaceListing.objects.filter(seller=user).order_by('-date_listed')
    
    context = {
        'profile_user': user,
        'listings': listings,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('users:profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(request.POST or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile_edit.html', context)




#_________________________________________________________________________________________________________________________