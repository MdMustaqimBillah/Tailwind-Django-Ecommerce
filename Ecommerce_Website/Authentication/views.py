from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from Authentication import forms, models
from django.contrib.auth.forms import PasswordChangeForm
from Profile.models import Profile
from Profile import views as profile_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
import re
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# Create your views here.

def sign_up(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('product_list'))
    else:
        form = forms.SignUpForm()
        if request.method == 'POST':
            form = forms.SignUpForm(request.POST)
            if form.is_valid():
                try:
                    # Create but don't save the user yet
                    user = form.save(commit=False)
                    user.is_active = False
                    
                    # Create the profile first to catch any potential errors
                    user_profile = Profile()
                    user_profile.first_name = form.cleaned_data.get('first_name')
                    user_profile.last_name = form.cleaned_data.get('last_name')
                    
                    # Now save the user since we know the profile is valid
                    user.save()
                    
                    # Link and save the profile
                    user_profile.user = user
                    user_profile.save()
                    
                    # Create verification token
                    verification = models.EmailVerification.objects.create(user=user)
                    
                    verification_url = request.build_absolute_uri(
                        reverse('Authentication:verify_email', args=[str(verification.token)])
                    )
                    
                    try:
                        # Separate try block for email sending
                        send_mail(
                            'Verify your email',
                            f'Click the link to verify your email: {verification_url}',
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                    except Exception as email_error:
                        # If email fails, delete everything and raise the error
                        user.delete()  # This will cascade delete the profile and verification
                        raise email_error
                    
                    messages.success(request, 'Please check your email to verify your account.')
                    return HttpResponseRedirect(reverse('Authentication:user_login'))
                    
                except Exception as e:
                    messages.error(request, f'Registration failed. Please try again. Error: {str(e)}')
            else:
                messages.error(request, 'Invalid form data. Please check the errors below.')   

    return render(request, 'Authentication/sign_up.html', {'form': form})

def verify_email(request, token):
    try:
        # Find verification record by token
        verification = models.EmailVerification.objects.get(token=token)
        
        # Check if link is still valid
        if verification.is_valid():
            user = verification.user
            # Activate user and mark email as verified
            user.is_active = True
            user.email_verified = True
            user.save()
            # Remove verification record
            verification.delete()
            messages.success(request, 'Email verified successfully. You can now login.')
        else:
            messages.error(request, 'Verification link has expired.')
            return HttpResponseRedirect(reverse('Authentication:resend_verification'))
    except models.EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return HttpResponseRedirect(reverse('Authentication:resend_verification'))
    
    return HttpResponseRedirect(reverse('Authentication:user_login'))



def user_login(request):
    if request.user.is_authenticated:

        if not request.user.user_profile.is_fully_filled():
            messages.warning(request, 'Please complete your profile details.')
            return HttpResponseRedirect(reverse('Profile:profile_setup'))

        return HttpResponseRedirect(reverse('product_list'))
    
    form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            # Check if email is verified before allowing login
            if user is None:
                messages.error(request, 'invalid email or password or both.')
                return HttpResponseRedirect(reverse('Authentication:user_login'))
            elif not user.email_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return HttpResponseRedirect(reverse('Authentication:resend_verification'))
            else:            
                login(request, user)
                if not user.user_profile.is_fully_filled():
                    messages.warning(request, 'Please fill in your profile details.')
                    return HttpResponseRedirect(reverse('Profile:profile_setup'))
                
                messages.success(request, 'Welcome for happy shopping!')
                return HttpResponseRedirect(reverse('product_list'))
                
                
            
    return render(request, 'Authentication/login.html', {'form': form})


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Find unverified user by email
            user = models.User.objects.get(email=email, email_verified=False)
            
            # Remove old verification tokens
            models.EmailVerification.objects.filter(user=user).delete()
            
            # Create new verification
            verification = models.EmailVerification.objects.create(user=user)
            
            # Generate new verification URL
            verification_url = request.build_absolute_uri(
                reverse('Authentication:verify_email', args=[str(verification.token)])
            )
            
            # Send new verification email
            send_mail(
                'Verify your email',
                f'Click the link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Verification email has been resent.')
            return HttpResponseRedirect(reverse('Authentication:user_login'))

        except models.User.DoesNotExist:
            messages.error(request, 'No unverified user found with this email.')
        
    return render(request, 'Authentication/resend_verification.html')


@login_required
def user_logout(request):
    try:
        # Print out session and user details before logout
        print(f"Current user: {request.user}")
        print(f"User is authenticated: {request.user.is_authenticated}")
        print(f"Session keys: {request.session.keys()}")
        
        # Perform logout
        logout(request)
        
        # Clear session data explicitly
        request.session.flush()
        
        messages.success(request, 'Logged out successfully!')
        
        # Redirect to login page instead of product list
        return HttpResponseRedirect(reverse('Authentication:user_login'))
    
    except Exception as e:
        print(f"Logout error: {str(e)}")
        messages.error(request, f'Logout failed: {str(e)}')
        return HttpResponseRedirect(reverse('Authentication:user_login'))

@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return HttpResponseRedirect(reverse_lazy('product_list'))
        else:
            messages.error(request, 'Invalid form data. Please check the errors below.')
    
    return render(request, 'Authentication/change_password.html', {'form': form})



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = models.User.objects.get(email=email)
            
            # Remove any existing password reset requests
            models.PasswordReset.objects.filter(user=user).delete()
            
            # Create new password reset with auto-generated verification code
            password_reset = models.PasswordReset.objects.create(user=user)

            try:
                send_mail(
                    'Password Reset Verification',
                    f"Your verification code is {password_reset.verification_code}. Do not share this code with anyone.",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Check your email for verification code')
                return HttpResponseRedirect(reverse('Authentication:reset_password_code_check'))
            
            except Exception as email_error:
                # Use proper logging instead of print
                logger.error(f'Password reset email failed: {email_error}')
                messages.error(request, 'Email sending failed. Please try again.')
                
        except models.User.DoesNotExist:
            messages.error(request, 'No user found with this email.')
    
    return render(request, 'Authentication/forgot_password.html')



def reset_password_code_check(request):
    MAX_VERIFICATION_ATTEMPTS = 3
    
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        
        # Track verification attempts in session
        verification_attempts = request.session.get('verification_attempts', 0)
        
        if verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
            messages.error(request, 'Too many verification attempts. Please restart.')
            return HttpResponseRedirect(reverse('Authentication:forgot_password'))
        
        try:
            # Check for valid, non-expired password reset
            password_reset = models.PasswordReset.objects.get(
                verification_code=verification_code, 
                expires_at__gte=timezone.now()
            )
            
            # Increment attempts
            request.session['verification_attempts'] = verification_attempts + 1
            
            return HttpResponseRedirect(reverse('Authentication:reset_password', args=[str(password_reset.token)]))
        
        except models.PasswordReset.DoesNotExist:
            messages.error(request, 'Invalid or expired verification code.')
    
    return render(request, 'Authentication/code_check.html')

def reset_password(request, token):
    try:
        password_reset = models.PasswordReset.objects.get(
            token=token, 
            expires_at__gte=timezone.now()
        )
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'Authentication/reset_password.html', {'token': token})
            
            is_strong, strength_message = validate_password_strength(password1)
            if not is_strong:
                messages.error(request, strength_message)
                return render(request, 'Authentication/reset_password.html', {'token': token})
            
            user = password_reset.user
            user.set_password(password1)
            user.save()
            
            # Delete all password reset records for this user
            models.PasswordReset.objects.filter(user=user).delete()
            
            messages.success(request, 'Password reset successfully.')
            return HttpResponseRedirect(reverse('Authentication:user_login'))
        
        return render(request, 'Authentication/reset_password.html', {'token': token})
    
    except models.PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link.')
        return HttpResponseRedirect(reverse('Authentication:forgot_password'))

def validate_password_strength(password):

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
 
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Strong password"

def social_auth_error(request):
    messages.error(request, "An error occurred during social authentication. Please try again.")
    return HttpResponseRedirect(reverse('Authentication:user_login'))
