from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from .forms import EmailSignupForm, ProfileForm
from .models import Profile


def _safe_next_url(request):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return 'home'


def sign_up(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(_safe_next_url(request))
    else:
        form = EmailSignupForm()

    return render(request, 'sign_up.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })



def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(_safe_next_url(request))
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'next': request.POST.get('next') or request.GET.get('next', ''),
    })

def logout_confirm(request):
    return render(request, 'logout_confirm.html')


def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    profile_image_url = None
    if profile.pfp and profile.pfp.storage.exists(profile.pfp.name):
        profile_image_url = profile.pfp.url

    return render(request, 'profile.html', {
        'form': form,
        'profile': profile,
        'profile_image_url': profile_image_url,
    })
