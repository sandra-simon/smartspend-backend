import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_password_reset_email(
    recipient_email: str,
    reset_token: str,
) -> None:
    reset_link = (
        f"{settings.frontend_url}/reset-password"
        f"?token={reset_token}"
    )

    message = EmailMessage()

    message["Subject"] = "Reset your SmartSpend password"
    message["From"] = (
        f"{settings.smtp_from_name} "
        f"<{settings.smtp_from_email}>"
    )
    message["To"] = recipient_email

    message.set_content(
        f"""Hello,

We received a request to reset your SmartSpend password.

Use the link below to reset your password:

{reset_link}

This link will expire in 30 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
SmartSpend
"""
    )

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
    ) as smtp:
        smtp.send_message(message)