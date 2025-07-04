def send_password_reset_email_service(to_email : str, reset_link : str):
    from api.utils.email import send_email
    send_email(
        subject="Reset your password",
        to=to_email,
        body=f"Click here to reset your password: {reset_link}"
    )

def send_verification_email_service(to_email: str, verification_link: str):
    from api.utils.email import send_email
    send_email(
        subject="Verify your account",
        to=to_email,
        body=f"Click here to verify your account: {verification_link}"
    )