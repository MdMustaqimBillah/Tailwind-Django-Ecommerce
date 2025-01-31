from social_core.exceptions import AuthForbidden
from Authentication.models import User

def create_user_profile(backend, user, response, *args, **kwargs):
    from Profile.models import Profile
    
    if backend.name == 'google-oauth2':
        # Ensure user is created or updated
        user.is_social_user = True
        user.email_verified = True  # Google emails are pre-verified
        user.save()
        
        # Extract name from Google response
        first_name = response.get('given_name', '')
        last_name = response.get('family_name', '')
        
        # Create or update profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': first_name,
                'last_name': last_name
            }
        )
        
        # If profile already exists, update if empty
        if not created:
            if not profile.first_name:
                profile.first_name = first_name
            if not profile.last_name:
                profile.last_name = last_name
            profile.save()


def check_email_collision(backend, details, user=None, *args, **kwargs):
    email = details.get('email')
    
    if user is None:  # New social login
        existing_user = User.objects.filter(email=email).first()
        
        if existing_user:
            # If existing user is not a social user, update their account
            if not existing_user.is_social_user:
                existing_user.is_social_user = True
                existing_user.email_verified = True
                existing_user.save()
                return {'user': existing_user}
    
    return None