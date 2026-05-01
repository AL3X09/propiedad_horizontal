import io
import os
import qrcode
import base64

from typing import Union
from pydantic import AnyUrl
from urllib.parse import quote


from propiedad_horizontal.app.core.config import settings



def generate_qr_url(reservation_id: Union[int, str], token: str, base: Union[str, AnyUrl]) -> str:
    """
    Genera la URL completa del QR para la reserva.
    
    Args:
        reservation_id: ID único de la reserva
        token: Token de validación hexadecimal del QR
        base: URL base de la API
    
    Returns:
        URL completa formateada con el endpoint de escaneo
    """
    base_str = str(base)  # <- clave: castear el AnyUrl a str
    token_q = quote(token, safe="")  # evita problemas con caracteres especiales
    # La ruta real del router de reservas usa el prefijo /parking/reservations
    # (tal como define el archivo api/parking_reservations.py), así que debe
    # coincidir con ello para que el QR lleve al endpoint correcto.
    return f"{base_str.rstrip('/')}/parking/reservations/{reservation_id}/scan?token={token_q}"

def generate_qr_image(reservation_id: Union[int, str], token: str, base: Union[str, AnyUrl]):
    """
    Genera una imagen QR en formato PNG.
    
    Args:
        reservation_id: ID único de la reserva
        token: Token de validación hexadecimal del QR
        base: URL base de la API
    
    Returns:
        bytes: Contenido PNG de la imagen QR
    """
    data = generate_qr_url(reservation_id, token, base)
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_qr_base64(reservation_id: Union[int, str], token: str, base: Union[str, AnyUrl]) -> str:
    """
    Genera una imagen QR encodificada en base64 para embeber en HTML.
    
    Útil para incluir directamente en emails HTML sin necesidad de adjuntos.
    
    Args:
        reservation_id: ID único de la reserva
        token: Token de validación hexadecimal del QR
        base: URL base de la API
    
    Returns:
        str: String base64 con el prefijo data:image/png;base64, listo para usar en src de img
    """
    qr_bytes = generate_qr_image(reservation_id, token, base)
    qr_b64 = base64.b64encode(qr_bytes).decode("utf-8")
    return f"data:image/png;base64,{qr_b64}"


def generate_reservation_email_html(
    visitor_name: str,
    reservation_id: int,
    qr_base64: str,
    vehicle_code: str,
    vehicle_type: str,
    starts_at: str,
    ends_at: str,
    total_price: str,
    spot_number: str = "TBD",
) -> str:
    """
    Genera un HTML atractivo y profesional para el email de confirmación de reserva.
    
    Características:
    - Saludo personalizado al usuario
    - QR embebido directamente en el cuerpo (no como adjunto)
    - Información de la reserva bien organizada
    - Estilos CSS responsivos y modernos
    - Compatible con todos los clientes de email
    
    Args:
        visitor_name: Nombre completo del visitante
        reservation_id: ID único de la reserva
        qr_base64: String base64 de la imagen QR (obtenido con generate_qr_base64)
        vehicle_code: Placa o código del vehículo
        vehicle_type: Tipo de vehículo (CARRO, MOTO, CICLA, etc.)
        starts_at: Fecha y hora de inicio formateada (ej: "2026-03-05 14:30")
        ends_at: Fecha y hora de fin formateada (ej: "2026-03-05 18:30")
        total_price: Precio total formateado (ej: "$25.000 COP")
        spot_number: Número del puesto de parqueadero (default: "TBD")
    
    Returns:
        str: HTML completo listo para enviar como email
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmación de Reserva de Parqueadero</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: green;
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                color: #333;
                margin-bottom: 10px;
                line-height: 1.6;
            }}
            .greeting strong {{
                color: #667eea;
            }}
            .qr-section {{
                text-align: center;
                margin: 40px 0;
                padding: 30px;
                background: #f8f9ff;
                border-radius: 10px;
                border: 2px dashed #667eea;
            }}
            .qr-section p {{
                color: #666;
                margin: 0 0 20px 0;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .qr-image {{
                max-width: 250px;
                height: auto;
                margin: 0 auto;
                display: block;
                border-radius: 8px;
            }}
            .info-section {{
                margin-top: 40px;
                border-top: 2px solid #eee;
                padding-top: 30px;
            }}
            .info-title {{
                font-size: 16px;
                font-weight: 600;
                color: #333;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #667eea;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }}
            .info-item {{
                background: #f8f9ff;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .info-label {{
                font-size: 12px;
                color: #999;
                text-transform: uppercase;
                margin-bottom: 5px;
                letter-spacing: 0.5px;
            }}
            .info-value {{
                font-size: 16px;
                font-weight: 600;
                color: #333;
                word-break: break-all;
            }}
            .info-full {{
                grid-column: 1 / -1;
            }}
            .footer {{
                background: #f8f9ff;
                padding: 30px;
                text-align: center;
                color: #666;
                font-size: 12px;
                border-top: 1px solid #eee;
            }}
            .footer p {{
                margin: 8px 0;
                line-height: 1.6;
            }}
            .cta-button {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 14px;
                transition: transform 0.3s ease;
            }}
            .cta-button:hover {{
                transform: scale(1.05);
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
                font-size: 13px;
                color: #856404;
                line-height: 1.6;
            }}
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 0;
                    border-radius: 0;
                }}
                .info-grid {{
                    grid-template-columns: 1fr;
                }}
                .header {{
                    padding: 30px 20px;
                }}
                .content {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- HEADER -->
            <div class="header">
                <h1>🅿️ Confirmación de Reserva</h1>
                <p> 📱 Tu solución de parqueadero inteligente</p>
            </div>

            <!-- CONTENIDO PRINCIPAL -->
            <div class="content">
                <!-- SALUDO PERSONALIZADO -->
                <p class="greeting">
                    ¡Hola <strong>{visitor_name}</strong>! 👋
                </p>
                <p class="greeting">
                    Tu reserva de parqueadero ha sido confirmada exitosamente. 
                    A continuación encontrarás tous tus detalles y el código QR para escanear al llegar.
                </p>

                <!-- SECCIÓN QR -->
                <div class="qr-section">
                    <p>📱 Tu Código QR para Acceso</p>
                    <img src="{qr_base64}" alt="QR Code" class="qr-image">
                    <p style="color: #999; font-size: 12px; margin-top: 15px;">
                        Escanea este código con tu teléfono al llegar al parqueadero
                    </p>
                </div>

                <!-- INFORMACIÓN DE LA RESERVA -->
                <div class="info-section">
                    <h2 class="info-title">📋 Detalles de tu Reserva</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">ID Reserva</div>
                            <div class="info-value">#{reservation_id}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Puesto Asignado</div>
                            <div class="info-value">{spot_number}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Tipo de Vehículo</div>
                            <div class="info-value">{vehicle_type}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Placa / Código</div>
                            <div class="info-value">{vehicle_code.upper()}</div>
                        </div>
                        <div class="info-item info-full">
                            <div class="info-label">Fecha y Hora Inicio</div>
                            <div class="info-value">📅 {starts_at}</div>
                        </div>
                        <div class="info-item info-full">
                            <div class="info-label">Fecha y Hora Fin</div>
                            <div class="info-value">📅 {ends_at}</div>
                        </div>
                    </div>
                </div>

                <!-- ADVERTENCIA -->
                <div class="warning">
                    <strong>⚠️ Importante:</strong> Guarda este email o captura una pantalla del código QR. 
                    Lo necesitarás al momento de escanear tu entrada al parqueadero.
                </div>

                <!-- CTA -->
                <div style="text-align: center;">
                    <a href="{ str(settings.APP_HOST) + ":" + str(settings.APP_PORT) or "http://localhost:8001"}/parking" class="cta-button">
                        Ver Mis Reservas
                    </a>
                </div>
            </div>

            <!-- FOOTER -->
            <div class="footer">
                <p><strong>¿Preguntas o problemas?</strong></p>
                <p>Contacta a nuestro equipo de soporte a través de la app o responde a este email.</p>
                <p style="margin-top: 15px; border-top: 1px solid #ddd; padding-top: 15px;">
                    © 2026 Sistema de Reservas de Parqueadero. Todos los derechos reservados.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content
