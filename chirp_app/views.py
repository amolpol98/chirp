from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from chirp_app.forms import AuthenticateForm, UserCreateForm, ChirpForm
from chirp_app.models import Chirp
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

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

def get_latest(user):
    try:
        return user.chirp_set.order_by('-id')[0]
    except IndexError:
        return ''

@login_required
def users(request, username='', chirp_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        chirps = Chirp.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'chirps': chirps, })
        return render(request, 'user.html', {'user': user, 'chirps': chirps, 'follow': True, })
    users = User.objects.all().annotate(chirp_count=Count('chirp'))
    chirps = map(get_latest, users)
    obj = zip(users, chirps)
    chirp_form = chirp_form or ChirpForm()
    return render(request,
                  'profiles.html', {'obj': obj, 'next_url': '/users/', 'chirp_form': chirp_form, 'username': request.user.username, })

@login_required
def follow(request):
    if request.method == 'POST':
        follow_id = request.POST.get('follow', False)
        if follow_id:
            print "coming hee", follow_id
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return '/users/'
    return redirect('/users/')