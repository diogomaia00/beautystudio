from typing import Optional

from .models import User


def get_user_by_msisdn(msisdn: str) -> Optional[User]:
    """Return the user with this msisdn, or ``None`` if no account exists."""
    return User.objects.filter(msisdn=msisdn).first()
