from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import LoginForm, OTPForm, ProfileUpdateForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserOTP, Profile
import random

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is None:
                return redirect('login')
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user_otp, created = UserOTP.objects.get_or_create(user=user)
            user_otp.otp = otp
            user_otp.save()
            print(f"User: {user.username}, OTP: {otp}")
            request.session['pre_otp_user_id'] = user.id
            return redirect('otp_verify')

            # login(request, user)
            # return redirect('home')
            # if user:
            #     return HttpResponse(f'Welcome {user.username}')
            # else:
            #     return HttpResponse('Invalid Credentials')
    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def otp_verify_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    user_id = request.session['pre_otp_user_id']
    if not user_id:
        return redirect('login')

    user = User.objects.get(id=user_id)
    user_otp = UserOTP.objects.get(user=user)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            if otp == user_otp.otp:
                user_otp.otp = ''
                user_otp.save()
                login(request, user)
                del request.session['pre_otp_user_id']
                return redirect('home')
            else:
                form.add_error('otp', 'Invalid OTP')
    
    else:
        form = OTPForm()
    return render(request, 'otp_verify.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_update_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_update')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {'form': form})