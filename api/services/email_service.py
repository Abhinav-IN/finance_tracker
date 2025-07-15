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

def reminder_subscription_email_service(to_email : str, subscription_name : str, amount : int):
    from api.utils.email import send_email
    send_email(
        subject="Subscription Due Tomorrow",
        to=to_email,
        body=f"Your subscription '{subscription_name}' of ₹{amount} is due tomorrow!"
    )

def subscription_email_service(to_email : str, subscription_name : str, amount : int):
    from api.utils.email import send_email
    send_email(
        subject="Subscription Billed Today",
        to=to_email,
        body=f"We've billed ₹{amount} for '{subscription_name}' today and recorded it as an expense."
    )