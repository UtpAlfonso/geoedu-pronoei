import os
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / "config" / ".env")

GMAIL_USER     = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")
GMAIL_FROM     = os.getenv("GMAIL_FROM", "GeoEdu PRONOEI <noreply@geoedu.pe>")
APP_URL        = os.getenv("APP_URL", "https://geoedu-pronoei.vercel.app")


async def enviar_email(destinatario: str, asunto: str, html: str):
    """Envía un email HTML via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = GMAIL_FROM
    msg["To"]      = destinatario
    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=GMAIL_USER,
        password=GMAIL_PASSWORD,
    )


async def enviar_verificacion(destinatario: str, nombre: str, token: str):
    """Envía email de verificación de cuenta."""
    url  = f"{APP_URL}/modulo_auth/frontend/verify.html?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <div style="background:#1A3A5C;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
        <h1 style="color:white;margin:0;font-size:22px;">GeoEdu PRONOEI</h1>
        <p style="color:#B0C4DE;margin:6px 0 0;font-size:13px;">Sistema de Análisis Educativo</p>
      </div>
      <div style="background:white;padding:28px;border:1px solid #e5e5e5;border-top:none;">
        <h2 style="color:#1A3A5C;font-size:18px;">Hola, {nombre} 👋</h2>
        <p style="color:#555;font-size:14px;line-height:1.6;">
          Gracias por registrarte en GeoEdu PRONOEI. Para activar tu cuenta
          haz clic en el siguiente botón:
        </p>
        <div style="text-align:center;margin:28px 0;">
          <a href="{url}"
             style="background:#1A3A5C;color:white;padding:12px 32px;border-radius:6px;
                    text-decoration:none;font-size:15px;font-weight:600;">
            Verificar mi cuenta
          </a>
        </div>
        <p style="color:#aaa;font-size:12px;">
          Este enlace expira en 24 horas. Si no creaste esta cuenta, ignora este correo.
        </p>
      </div>
      <div style="background:#f8f8f8;padding:12px;border-radius:0 0 8px 8px;text-align:center;">
        <p style="color:#aaa;font-size:11px;margin:0;">
          © 2026 GeoEdu PRONOEI — Sistema de Análisis de Programas No Escolarizados
        </p>
      </div>
    </div>
    """
    await enviar_email(destinatario, "Verifica tu cuenta — GeoEdu PRONOEI", html)


async def enviar_recuperacion(destinatario: str, nombre: str, token: str):
    """Envía email de recuperación de contraseña."""
    url  = f"{APP_URL}/modulo_auth/frontend/reset.html?token={token}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
      <div style="background:#1A3A5C;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
        <h1 style="color:white;margin:0;font-size:22px;">GeoEdu PRONOEI</h1>
        <p style="color:#B0C4DE;margin:6px 0 0;font-size:13px;">Sistema de Análisis Educativo</p>
      </div>
      <div style="background:white;padding:28px;border:1px solid #e5e5e5;border-top:none;">
        <h2 style="color:#C62828;font-size:18px;">Recuperación de contraseña</h2>
        <p style="color:#555;font-size:14px;line-height:1.6;">
          Hola <strong>{nombre}</strong>, recibimos una solicitud para restablecer
          la contraseña de tu cuenta. Haz clic en el botón para crear una nueva:
        </p>
        <div style="text-align:center;margin:28px 0;">
          <a href="{url}"
             style="background:#C62828;color:white;padding:12px 32px;border-radius:6px;
                    text-decoration:none;font-size:15px;font-weight:600;">
            Restablecer contraseña
          </a>
        </div>
        <p style="color:#aaa;font-size:12px;">
          Este enlace expira en 1 hora. Si no solicitaste este cambio, ignora este correo.
        </p>
      </div>
      <div style="background:#f8f8f8;padding:12px;border-radius:0 0 8px 8px;text-align:center;">
        <p style="color:#aaa;font-size:11px;margin:0;">
          © 2026 GeoEdu PRONOEI — Sistema de Análisis de Programas No Escolarizados
        </p>
      </div>
    </div>
    """
    await enviar_email(destinatario, "Recuperar contraseña — GeoEdu PRONOEI", html)