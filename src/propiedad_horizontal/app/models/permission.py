from tortoise import fields, models

class Permission(models.Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=100, unique=True, index=True)  # ej: "users:read"
    description = fields.CharField(max_length=255, null=True)         # opcional

    roles = fields.ManyToManyField("models.Role", related_name="permissions")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "permissions"
        indexes = [("code",)]

    def __str__(self) -> str:
        return f"<Permission {self.code}>"