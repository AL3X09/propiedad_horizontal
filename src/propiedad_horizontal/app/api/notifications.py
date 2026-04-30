"""
API endpoints para envío de notificaciones (email y SMS).
Estos endpoints actúan como proxy hacia el servicio de notificaciones externo.
Requieren autenticación JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from propiedad_horizontal.app.services.notification_client import notification_client
from propiedad_horizontal.app.core.auth import get_current_user
from pydantic import BaseModel, EmailStr, validator
import re


router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "No encontrado"}},
)


class EmailNotificationSchema(BaseModel):
    """Schema para envío de email."""
    to_email: EmailStr
    subject: str
    html_content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "to_email": "usuario@ejemplo.com",
                "subject": "Notificación",
                "html_content": "<p>Contenido del mensaje</p>"
            }
        }


class SMSNotificationSchema(BaseModel):
    """Schema para envío de SMS."""
    to_number: str
    message_body: str
    
    @validator('to_number')
    def validate_phone_number(cls, v):
        # Validación E.164: + seguido de 1-15 dígitos
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('El número debe estar en formato E.164 (ej: +573001234567)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "to_number": "+573001234567",
                "message_body": "Su mensaje de notificación"
            }
        }


@router.post(
    "/email",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar email",
    description="Envía un email mediante el servicio de notificaciones. Requiere autenticación JWT.",
    response_description="Email aceptado para envío",
)
async def send_email_notification(
    email_data: EmailNotificationSchema,
    current_user = Depends(get_current_user),
):
    """
    Endpoint para enviar notificaciones por email.
    
    Requiere token JWT en el header Authorization.
    Solo usuarios autenticados pueden enviar emails.
    """
    try:
        resultado = await notification_client.enviar_email(
            to_email=email_data.to_email,
            subject=email_data.subject,
            html_content=email_data.html_content
        )
        return {
            "mensaje": "Email aceptado para envío",
            "detalles": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar email: {str(e)}"
        )


@router.post(
    "/sms",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar SMS",
    description="Envía un SMS mediante el servicio de notificaciones. Requiere autenticación JWT.",
    response_description="SMS aceptado para envío",
)
async def send_sms_notification(
    sms_data: SMSNotificationSchema,
    current_user = Depends(get_current_user),
):
    """
    Endpoint para enviar notificaciones por SMS.
    
    Requiere token JWT en el header Authorization.
    Solo usuarios autenticados pueden enviar SMS.
    """
    try:
        resultado = await notification_client.enviar_sms(
            to_number=sms_data.to_number,
            message_body=sms_data.message_body
        )
        return {
            "mensaje": "SMS aceptado para envío",
            "detalles": resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar SMS: {str(e)}"
        )
