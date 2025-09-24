# core/utils.py

def is_privileged_user(user):
    """Checks if a user is a Superuser or has the MANAGEMENT role."""
    return user.is_authenticated and (user.is_superuser or user.role == 'MANAGEMENT')