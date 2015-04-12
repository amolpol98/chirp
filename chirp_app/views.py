from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from chirp_app.forms import AuthenticateForm, UserCreateForm, ChirpForm
from chirp_app.models import Chirp
from django.contrib.auth.decorators import login_required

def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        chirp_form = ChirpForm()
        user = request.user
        chirps_self = Chirp.objects.filter(user=user.id)
        chirps_buddies = Chirp.objects.filter(user__userprofile__in=user.profile.follows.all)
        chirps = chirps_self | chirps_buddies

        return render(request,
                      'buddies.html',
                      {'chirp_form': chirp_form, 'user': user,
                       'chirps': chirps,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()

        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')

def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')

@login_required
def submit(request):
    if request.method == 'POST':
        chirp_form = ChirpForm(data=request.POST)
        next_url = request.POST.get('next_url', '/')
        if chirp_form.is_valid():
            chirp = chirp_form.save(commit=False)
            chirp.user = request.user
            chirp.save()
            return redirect('/')
        else:
            return public(request, chirp_form)
    return redirect('/')

@login_required
def public(request, chirp_form=None):
    chirp_form = chirp_form or ChirpForm()
    chirps = Chirp.objects.reverse()[:10]
    return render(request,
                  'public.html', {'chirp_form': chirp_form, 'next_url': '/chirps', 'chirps': chirps, 'username': request.user.username})