def verification_email(link: str) -> tuple[str, str]:
    """Return (subject, body) for the email-verification message."""
    subject = "Verify your TripMate email"
    body = (
        "Welcome to TripMate!\n\n"
        "Please verify your email address by clicking the link below:\n"
        f"{link}\n\n"
        "If you didn't create a TripMate account, you can ignore this email."
    )
    return subject, body


def password_reset_email(link: str) -> tuple[str, str]:
    """Return (subject, body) for the password-reset message."""
    subject = "Reset your TripMate password"
    body = (
        "We received a request to reset your TripMate password.\n\n"
        "Click the link below to choose a new password. This link expires "
        "in 15 minutes:\n"
        f"{link}\n\n"
        "If you didn't request this, you can safely ignore this email - "
        "your password will not be changed."
    )
    return subject, body


def admin_invite_email(link: str) -> tuple[str, str]:
    """Return (subject, body) for the admin-account-invite message."""
    subject = "You've been added as a TripMate admin"
    body = (
        "An account has been created for you on TripMate.\n\n"
        "Click the link below to set your password. This link expires "
        "in 48 hours:\n"
        f"{link}\n\n"
        "If you weren't expecting this, you can safely ignore this email."
    )
    return subject, body
