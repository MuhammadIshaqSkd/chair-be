from rest_framework_simplejwt.tokens import RefreshToken

def get_normalized_email(email):
    local_part, domain_part = email.lower().split('@')
    return f"{local_part.replace('.', '')}@{domain_part}"

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
    }
