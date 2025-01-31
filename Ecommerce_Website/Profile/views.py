import random
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from Profile.models import Profile, NumberVerification, PhoneNumber, NameChanger
from Cart.models import UserOrder, TotalOrder
from django.contrib.auth.decorators import login_required
from Profile.forms import UserProfileForm, PhoneNumberForm, UpdateNameForm
from django.utils import timezone


@login_required
def profile(request):
    user=request.user
    profile = Profile.objects.get(user=request.user)
    if user.is_superuser:
        total_order = TotalOrder.objects.first()
        total_order = total_order.count if total_order else 0
    else:
        user_order = UserOrder.objects.get_or_create(user=request.user)
        total_order = user_order[0].count

    context = {
        'profile': profile,
        'total_order': total_order,
    }
    return render(request, 'Profile/profile.html', context=context)


@login_required
def profile_setup(request):
    try:
        profile = Profile.objects.get(user=request.user)
        form = UserProfileForm(instance=profile)
    except Profile.DoesNotExist:
        form = UserProfileForm()
    
    if request.method == 'POST':
        if profile:
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = UserProfileForm(request.POST, request.FILES)
            
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('Profile:profile')
        else:
            messages.error(request, "Profile update failed. Please check the errors below.")
    
    return render(request, 'Profile/profile_setup.html', {'form': form})


@login_required
def verification_view(request):
    try:
        phone_instance = PhoneNumber.objects.get(user=request.user)
        form = PhoneNumberForm(instance=phone_instance)
    except PhoneNumber.DoesNotExist:
        form = PhoneNumberForm()

    if request.method == 'POST':
        if hasattr(request.user, 'user_phone_number'):
            form = PhoneNumberForm(request.POST, instance=request.user.user_phone_number)
        else:
            form = PhoneNumberForm(request.POST)

        if form.is_valid():
            phone_number = form.save(commit=False)
            phone_number.user = request.user
            phone_number.save()

            success, error_message = initiate_phone_verification(request.user)
            
            if success:
                messages.success(request, "Verification code sent successfully!")
                return redirect('Profile:verify_code', phone_number=phone_number.phone_number.as_e164)
            else:
                messages.error(request, f"Failed to send verification code: {error_message}")
                return redirect('Profile:resend_code')
    
    return render(request, 'Profile/verification.html', {'form': form})


def generate_verification_code():
    return str(random.randint(100000, 999999))



def send_verification_sms(phone_number, code):
    """
    Send SMS using Bulk SMS BD API
    """
    try:
        url = "http://bulksmsbd.net/api/smsapi"
        payload = {
            'api_key': settings.BULKSMS_API_KEY,
            'type': 'text',
            'number': str(phone_number),
            'senderid': settings.BULKSMS_SENDER_ID,
            'message': f"Dear Customer,\nYour verification code is: {code}.\nDon't share your verification code with anyone.\nPlease don't reply to this message, it is computer generated.\nThank you.\n\nRegards,\nAi-reen."
        }
        
        response = requests.post(url, data=payload)
        print(f"SMS API Response: {response.text}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                response_code = response_data.get('response_code')
                
                # Success case
                if response_code == 202:
                    return True, "SMS sent successfully"
                
                # Handle specific error cases
                error_messages = {
                    1001: "Invalid phone number",
                    1002: "Invalid or disabled sender ID",
                    1003: "Missing required fields",
                    1005: "Internal server error",
                    1006: "Balance validity expired",
                    1007: "Insufficient balance",
                    1011: "User ID not found",
                    1012: "Masking SMS must be in Bengali",
                    1013: "Invalid sender ID for this API key",
                    1014: "Invalid sender type",
                    1015: "No valid gateway found for sender ID",
                    1016: "Price information not found for sender ID",
                    1017: "Price information not found for sender type",
                    1018: "Account is disabled",
                    1019: "Sender type price is disabled",
                    1020: "Parent account not found",
                    1021: "Parent account price not found",
                    1031: "Account not verified",
                    1032: "IP not whitelisted. Please contact administrator to whitelist IP: 103.176.81.100"
                }
                
                error_message = error_messages.get(response_code, 
                                                 response_data.get('error_message', 'Unknown error'))
                return False, error_message
                
            except ValueError:
                return False, "Invalid response from SMS gateway"
        return False, f"HTTP Error: {response.status_code}"
        
    except Exception as e:
        print(f"SMS sending error: {str(e)}")
        return False, str(e)    


def initiate_phone_verification(user):
    """
    Generate and send verification code
    """
    verification_code = generate_verification_code()
    print(f"Generated code: {verification_code}")
    
    try:
        verification, created = NumberVerification.objects.get_or_create(
            user=user,
            defaults={
                'verification_code': verification_code,
            }
        )

        print( f"Numberverification object status created:{created}")

        if not created:
            verification.verification_code = verification_code
            verification.save()
        
        phone_number = user.user_phone_number.phone_number
        print(f"Sending SMS to: {phone_number}")
        
        success, error_message = send_verification_sms(phone_number, verification_code)
        print(f"SMS send result - Success: {success}, Error: {error_message}")
        
        if not success:
            verification.delete()
            
        return success, error_message
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return False, str(e)


@login_required
def verify_code(request, phone_number):
    """
    Verify the submitted code
    """
    print("Verify Code......function......")

    if request.method == 'POST':
        code = request.POST.get('code')
        is_valid = verify_phone_number(user=request.user, code=code)

        print(f"Verification result in verified code function - Valid: {is_valid}")
        
        try:
            verification_model = NumberVerification.objects.get(user=request.user)
            
            if is_valid:
                number_model = PhoneNumber.objects.get(user=request.user, phone_number=phone_number)
                number_model.is_verified = True
                number_model.save()
                verification_model.delete()
                
                messages.success(request, "Phone number verified successfully!")
                return redirect('Profile:profile')
            else:
                messages.error(request, "Invalid  verification code!")
                
        except NumberVerification.DoesNotExist:
            messages.error(request, "Verification code not found!")
    
    return render(request, 'Profile/verify_code.html')


def verify_phone_number(user, code):
    """
    Check if the verification code is valid
    """

    print(f'Verifying phone number...........')

    try:
        verification = NumberVerification.objects.get(user=user)

        print(f" NumberVerification model is valid : {verification.is_valid()} verification code: {verification.verification_code}")

        print(f'expires at: {verification.expires_at}  current time: {timezone.now()} created at: {verification.created_at}')

        print(f"code : {code} verification code: {verification.verification_code}")
        
        if verification.is_valid() and verification.verification_code == code:
            return True
        print("Went through here >>>>>>>>>>")
        return False
        
    except NumberVerification.DoesNotExist:
        return False


@login_required   
def resend_code(request):
    user = request.user
    try:
        phone_number = PhoneNumber.objects.get(user=user)
        if request.method == 'POST':
            success, error_message = initiate_phone_verification(user)
            
            if success:
                messages.success(request, "Verification code sent successfully!")
                return redirect('Profile:verify_code', phone_number=phone_number.phone_number.as_e164)
            else:
                messages.error(request, f"Failed to send verification code: {error_message}")
    except PhoneNumber.DoesNotExist:
        messages.error(request, "Phone number not found")
    
    return redirect('Profile:verification')
    



def change_name(request):
    user = request.user
    form = UpdateNameForm(instance=user)
    if request.method == 'POST':
        try:
            name_changer = NameChanger.objects.get(user=user)

            if not name_changer.is_valid():
                messages.error(request, "You have already changed your name within 60 days!")
                return redirect('Profile:profile')
            
        except NameChanger.DoesNotExist:
            name_changer = NameChanger.objects.create(user=user)
            name_changer.save()

        form = UpdateNameForm(request.POST, instance=user.user_profile)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Name updated successfully!")
            return redirect('Profile:profile')
    return render(request, 'Profile/change_name.html', {'form': form})