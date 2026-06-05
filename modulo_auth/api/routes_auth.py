import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from config.db import get_connection
from modulo_auth.core.security import (
    hash_password, verify_password,
    create_access_token, decode_token, generate_token
)
from modulo_auth.core.email import enviar_verificacion, enviar_recuperacion

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    nombre:   str
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class RecoverRequest(BaseModel):
    email: EmailStr

class ResetRequest(BaseModel):
    token:        str
    new_password: str


# ── Helpers BD ───────────────────────────────────────────────

def get_user_by_email(email: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            return cur.fetchone()
    finally:
        conn.close()

def get_user_by_token_verificacion(token: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE token_verificacion = %s", (token,))
            return cur.fetchone()
    finally:
        conn.close()

def get_user_by_token_recuperacion(token: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM usuarios WHERE token_recuperacion = %s AND token_expira > NOW()",
                (token,)
            )
            return cur.fetchone()
    finally:
        conn.close()


# ── Endpoints ────────────────────────────────────────────────

@router.post("/register")
async def register(body: RegisterRequest):
    """Registra un nuevo usuario y envía email de verificación."""
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    token = generate_token()
    hashed = hash_password(body.password)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, token_verificacion)
                VALUES (%s, %s, %s, %s)
            """, (body.nombre, body.email, hashed, token))
        conn.commit()
    finally:
        conn.close()

    try:
        await enviar_verificacion(body.email, body.nombre, token)
    except Exception as e:
        print(f"Error enviando email: {e}")

    return {
        "mensaje": "Cuenta creada. Revisa tu correo para verificar tu cuenta.",
        "email": body.email
    }


@router.get("/verify")
def verify_account(token: str):
    """Verifica la cuenta con el token enviado por email."""
    usuario = get_user_by_token_verificacion(token)
    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido o ya utilizado.")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET activo = TRUE, token_verificacion = NULL
                WHERE id = %s
            """, (usuario["id"],))
        conn.commit()
    finally:
        conn.close()

    return {"mensaje": "Cuenta verificada correctamente. Ya puedes iniciar sesión."}


@router.post("/login")
def login(body: LoginRequest):
    """Inicia sesión y retorna JWT."""
    usuario = get_user_by_email(body.email)

    if not usuario or not verify_password(body.password, usuario["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos."
        )

    if not usuario["activo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta no verificada. Revisa tu correo."
        )

    # Actualizar último acceso
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s",
                (usuario["id"],)
            )
        conn.commit()
    finally:
        conn.close()

    token = create_access_token({
        "sub":    str(usuario["id"]),
        "email":  usuario["email"],
        "nombre": usuario["nombre"],
        "rol":    usuario["rol"],
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "nombre":       usuario["nombre"],
        "email":        usuario["email"],
        "rol":          usuario["rol"],
    }


@router.post("/recover")
async def recover_password(body: RecoverRequest):
    """Envía email de recuperación de contraseña."""
    usuario = get_user_by_email(body.email)

    # Siempre responder lo mismo para no revelar si el email existe
    if not usuario:
        return {"mensaje": "Si el correo existe, recibirás un enlace de recuperación."}

    token   = generate_token()
    expira  = datetime.utcnow() + timedelta(hours=1)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET token_recuperacion = %s, token_expira = %s
                WHERE id = %s
            """, (token, expira, usuario["id"]))
        conn.commit()
    finally:
        conn.close()

    try:
        await enviar_recuperacion(body.email, usuario["nombre"], token)
    except Exception as e:
        print(f"Error enviando email recuperación: {e}")

    return {"mensaje": "Si el correo existe, recibirás un enlace de recuperación."}


@router.post("/reset-password")
def reset_password(body: ResetRequest):
    """Restablece la contraseña con el token de recuperación."""
    usuario = get_user_by_token_recuperacion(body.token)
    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    nuevo_hash = hash_password(body.new_password)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET password_hash = %s,
                    token_recuperacion = NULL,
                    token_expira = NULL
                WHERE id = %s
            """, (nuevo_hash, usuario["id"]))
        conn.commit()
    finally:
        conn.close()

    return {"mensaje": "Contraseña restablecida correctamente. Ya puedes iniciar sesión."}


@router.get("/me")
def get_me(authorization: str = None):
    """Retorna datos del usuario autenticado a partir del JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado.")

    token   = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    return {
        "id":     payload.get("sub"),
        "email":  payload.get("email"),
        "nombre": payload.get("nombre"),
        "rol":    payload.get("rol"),
    }