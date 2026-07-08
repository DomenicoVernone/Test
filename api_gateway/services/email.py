import logging

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from core.config import settings

logger = logging.getLogger(__name__)

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
)


async def send_reset_email(email: str, token: str) -> None:
    frontend_url = "http://localhost:5173"
    reset_link = f"{frontend_url}/reset-password?token={token}"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
        <h2 style="color: #3b82f6;">Recupero Password</h2>
        <p>Hai richiesto il reset della password per il tuo account MLOps Clinical.</p>
        <p>Clicca il bottone qui sotto per impostare una nuova password:</p>
        <a href="{reset_link}"
           style="display: inline-block; padding: 12px 24px;
                  background-color: #3b82f6; color: white;
                  text-decoration: none; border-radius: 6px;
                  margin: 16px 0;">
           Reimposta Password
        </a>
        <p style="color: #666; font-size: 13px;">
            Il link scade tra 1 ora.<br>
            Se non hai richiesto il reset, ignora questa email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee;">
        <p style="color: #999; font-size: 12px;">
            MLOps Clinical &mdash; Progetto di ricerca accademica
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Recupero password — MLOps Clinical",
        recipients=[email],
        body=html,
        subtype="html",
    )

    try:
        fm = FastMail(_conf)
        await fm.send_message(message)
        logger.info(f"Email reset inviata a {email}")
    except Exception:
        logger.exception(f"Errore invio email reset a {email}")
