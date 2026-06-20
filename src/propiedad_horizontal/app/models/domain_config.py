"""
Modelo de dominios, del aplicativo.

Registra el dominio activo en cuel esta escuchando el sistema.
"""
from tortoise import fields, models

class DomainConfig(models.Model):
    id = fields.IntField(pk=True)
    domain = fields.CharField(max_length=255, unique=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "domain_config"
        indexes = [("is_active",)]

    def __str__(self) -> str:
        return f"<Dominio id={self.id} domain={self.domain} active={self.is_active}>"