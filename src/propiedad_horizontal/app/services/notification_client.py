"""
Servicio cliente para consumir el servicio externo de notificaciones.
Expone funcionalidades de envío de email y SMS mediante llamadas HTTP
al servicio de notificaciones configurado en settings.
"""

import httpx
from fastapi import BackgroundTasks
from typing import Optional
from propiedad_horizontal.app.core.config import settings


class NotificationClient:
    """
    Cliente HTTP para el servicio de notificaciones.
    Maneja envío de emails y SMS mediante API REST.
    """
    
    def __init__(self):
        self.base_url = settings.NOTIFICACIONES_SERVICE_URL
        self.api_key = settings.NOTIFICACIONES_API_KEY
        self.headers = {"X-API-Key": self.api_key}
    
    async def enviar_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str
    ) -> dict:
        """
        Envía un email mediante el servicio de notificaciones.
        
        Args:
            to_email: Dirección de correo destinatario
            subject: Asunto del email
            html_content: Contenido HTML del email
            
        Returns:
            dict: Respuesta del servicio de notificaciones
            
        Raises:
            httpx.HTTPStatusError: Si el servicio retorna error
        """
        url = f"{self.base_url}/email/enviar"
        payload = {
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=payload, 
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def enviar_sms(
        self, 
        to_number: str, 
        message_body: str
    ) -> dict:
        """
        Envía un SMS mediante el servicio de notificaciones.
        
        Args:
            to_number: Número de teléfono en formato E.164 (ej: +573001234567)
            message_body: Cuerpo del mensaje SMS
            
        Returns:
            dict: Respuesta del servicio de notificaciones
            
        Raises:
            httpx.HTTPStatusError: Si el servicio retorna error
        """
        url = f"{self.base_url}/sms/enviar"
        payload = {
            "to_number": to_number,
            "message_body": message_body
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, 
                json=payload, 
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()


# Instancia singleton para uso en la aplicación
notification_client = NotificationClient()

