"""
Utilidades para renderizar templates de email.

Este módulo proporciona funciones para cargar y renderizar templates HTML
de email de forma segura y limpia, sin embeberlos en el código de servicios.
"""

from pathlib import Path
from typing import Dict, Any


def _load_template(template_name: str) -> str:
    """
    Carga un archivo de template HTML.
    
    Args:
        template_name: Nombre del archivo (ej: 'checkout_receipt.html')
    
    Returns:
        Contenido del archivo de template
    
    Raises:
        FileNotFoundError: Si el template no existe
    """
    template_dir = Path(__file__).parent / "email_templates"
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template no encontrado: {template_name} en {template_dir}"
        )
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def _simple_template_render(template: str, context: Dict[str, Any]) -> str:
    """
    Renderiza un template reemplazando variables del tipo {{ variable }}.
    
    Esta es una implementación simple que no requiere dependencias externas.
    Para casos complejos, considera usar Jinja2.
    
    Args:
        template: Contenido HTML del template
        context: Dict con variables a reemplazar
    
    Returns:
        HTML renderizado con variables reemplazadas
    """
    result = template
    for key, value in context.items():
        placeholder = "{{ " + key + " }}"
        result = result.replace(placeholder, str(value))
    return result


def render_checkout_email(
    visitor_name: str,
    reservation_id: int,
    spot_number: str,
    starts_at_formatted: str,
    ends_at_formatted: str,
    price_breakdown: str,
    total_price_formatted: str,
) -> str:
    """
    Renderiza el email de recibo de checkout (salida del parqueadero).
    
    Args:
        visitor_name: Nombre del visitante
        reservation_id: ID de la reserva
        spot_number: Número/código del puesto de parqueadero
        starts_at_formatted: Hora de entrada formateada (ej: "10/03/2026 a las 14:30")
        ends_at_formatted: Hora de salida formateada
        price_breakdown: Desglose del cálculo de precio (multilinea)
        total_price_formatted: Precio total formateado (ej: "$15,000 COP")
    
    Returns:
        HTML del email listo para enviar
    """
    template = _load_template("checkout_receipt.html")
    context = {
        "visitor_name": visitor_name,
        "reservation_id": reservation_id,
        "spot_number": spot_number,
        "starts_at_formatted": starts_at_formatted,
        "ends_at_formatted": ends_at_formatted,
        "price_breakdown": price_breakdown,
        "total_price_formatted": total_price_formatted,
    }
    return _simple_template_render(template, context)


def render_reservation_confirmation(
    visitor_name: str,
    reservation_id: int,
    qr_base64: str,
    spot_number: str,
    vehicle_code: str,
    vehicle_type: str,
    starts_at: str,
    ends_at: str,
    total_price: str,
) -> str:
    """
    Renderiza el email de confirmación de reserva (con QR).
    
    Args:
        visitor_name: Nombre del visitante
        reservation_id: ID de la reserva
        qr_base64: Código QR en base64 para embeberlo en la imagen
        spot_number: Número/código del puesto de parqueadero
        vehicle_code: Placa del vehículo
        vehicle_type: Tipo de vehículo (ej: "🏎️ Carro")
        starts_at: Hora de entrada formateada
        ends_at: Hora de salida formateada
        total_price: Precio total formateado
    
    Returns:
        HTML del email listo para enviar
    """
    template = _load_template("reservation_confirmation.html")
    context = {
        "visitor_name": visitor_name,
        "reservation_id": reservation_id,
        "qr_base64": qr_base64,
        "spot_number": spot_number,
        "vehicle_code": vehicle_code,
        "vehicle_type": vehicle_type,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "total_price": total_price,
    }
    return _simple_template_render(template, context)
