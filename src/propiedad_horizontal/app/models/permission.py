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
        return f"<Permiso {self.code}>"
    
    @classmethod
    async def seed_defaults(cls):
        """
        Solo crea registros si no existen.
        """
        defaults = [
            {"code":"vinculosinteriorcasa:view", "description": "Permiso para acceder a vínculos de la casa"},
            {"code":"vinculosinteriorcasa:read", "description": "Permiso para leer vínculos de la casa"},
            {"code":"vinculosinteriorcasa:write", "description": "Permiso para escribir vínculos de la casa"},
            {"code":"vinculosinteriorcasa:delete", "description": "Permiso para eliminar vínculos de la casa"},
            {"code":"bienes:view", "description": "Permiso para acceder a bienes"},
            {"code":"bienes:read", "description": "Permiso para leer bienes"},
            {"code":"bienes:write", "description": "Permiso para escribir bienes"},
            {"code":"bienes:delete", "description": "Permiso para eliminar bienes"},
            {"code":"casaapartamentos:view", "description": "Permiso para acceder a casas de apartamentos"},
            {"code":"casaapartamentos:read", "description": "Permiso para leer casas de apartamentos"},
            {"code":"casaapartamentos:write", "description": "Permiso para escribir casas de apartamentos"},
            {"code":"casaapartamentos:delete", "description": "Permiso para eliminar casas de apartamentos"},
            {"code":"dominios:view", "description": "Permiso para acceder a dominios"},
            {"code":"dominios:read", "description": "Permiso para leer dominios"},
            {"code":"dominios:write", "description": "Permiso para escribir dominios"},
            {"code":"dominios:delete", "description": "Permiso para eliminar dominios"},
            {"code":"asignarparqueaderos:view", "description": "Permiso para acceder a asignaciones de parqueaderos"},
            {"code":"asignarparqueaderos:read", "description": "Permiso para asignar parqueaderos"},
            {"code":"asignarparqueaderos:write", "description": "Permiso para escribir asignaciones de parqueaderos"},
            {"code":"asignarparqueaderos:delete", "description": "Permiso para eliminar asignaciones de parqueaderos"},
            {"code":"loteriaparqueadero:view", "description": "Permiso para acceder a lotería de parqueadero"},
            {"code":"loteriaparqueadero:read", "description": "Permiso para leer lotería de parqueadero"},
            {"code":"loteriaparqueadero:write", "description": "Permiso para escribir lotería de parqueadero"},
            {"code":"loteriaparqueadero:delete", "description": "Permiso para eliminar lotería de parqueadero"},
            {"code":"loteriaparqueadero:execute", "description": "Permiso para ejecutar lotería de parqueadero"},
            {"code":"reservaparqueaderos:view", "description": "Permiso para acceder a reservas de parqueaderos"},
            {"code":"reservaparqueaderos:read", "description": "Permiso para leer reservas de parqueaderos"},
            {"code":"reservaparqueaderos:write", "description": "Permiso para escribir reservas de parqueaderos"},
            {"code":"reservaparqueaderos:delete", "description": "Permiso para eliminar reservas de parqueaderos"},
            {"code":"parqueaderos:view", "description": "Permiso para acceder a parqueaderos"},
            {"code":"parqueaderos:read", "description": "Permiso para leer parqueaderos"},
            {"code":"parqueaderos:write", "description": "Permiso para escribir parqueaderos"},
            {"code":"parqueaderos:delete", "description": "Permiso para eliminar parqueaderos"},
            {"code":"permisos:view", "description": "Permiso para acceder a permisos"},
            {"code":"permisos:read", "description": "Permiso para leer permisos"},
            {"code":"permisos:write", "description": "Permiso para escribir permisos"},
            {"code":"permisos:delete", "description": "Permiso para eliminar permisos"},
            {"code":"personas:view", "description": "Permiso para acceder a personas"},
            {"code":"personas:read", "description": "Permiso para leer personas"},
            {"code":"personas:write", "description": "Permiso para escribir personas"},
            {"code":"personas:delete", "description": "Permiso para eliminar personas"},
            {"code":"ph:view", "description": "Permiso para acceder a propiedad horizontal"},
            {"code":"ph:read", "description": "Permiso para leer propiedad horizontal"},
            {"code":"ph:write", "description": "Permiso para escribir propiedad horizontal"},
            {"code":"ph:delete", "description": "Permiso para eliminar propiedad horizontal"},
            {"code":"roles:view", "description": "Permiso para acceder a roles"},
            {"code":"roles:read", "description": "Permiso para leer roles"},
            {"code":"roles:write", "description": "Permiso para escribir roles"},
            {"code":"roles:delete", "description": "Permiso para eliminar roles"},
            {"code":"torreinteriores:view", "description": "Permiso para acceder a torres interiores"},
            {"code":"torreinteriores:read", "description": "Permiso para leer torres interiores"},
            {"code":"torreinteriores:write", "description": "Permiso para escribir torres interiores"},
            {"code":"torreinteriores:delete", "description": "Permiso para eliminar torres interiores"},
            {"code":"trasteos:view", "description": "Permiso para acceder a trasteos"},
            {"code":"trasteos:read", "description": "Permiso para leer trasteos"},
            {"code":"trasteos:write", "description": "Permiso para escribir trasteos"},
            {"code":"trasteos:delete", "description": "Permiso para eliminar trasteos"},
            {"code":"usuariopermisos:view", "description": "Permiso para acceder a permisos de usuarios"},
            {"code":"usuariopermisos:read", "description": "Permiso para leer permisos de usuarios"},
            {"code":"usuariopermisos:write", "description": "Permiso para escribir permisos de usuarios"},
            {"code":"usuariopermisos:delete", "description": "Permiso para eliminar permisos de usuarios"},
            {"code":"usuarios:view", "description": "Permiso para acceder a usuarios"},
            {"code":"usuarios:read", "description": "Permiso para leer usuarios"},
            {"code":"usuarios:write", "description": "Permiso para escribir usuarios"},
            {"code":"usuarios:delete", "description": "Permiso para eliminar usuarios"},
            {"code":"tipovehiculos:view", "description": "Permiso para acceder a tipos de vehículos"},
            {"code":"tipovehiculos:read", "description": "Permiso para leer tipos de vehículos"},
            {"code":"tipovehiculos:write", "description": "Permiso para escribir tipos de vehículos"},
            {"code":"tipovehiculos:delete", "description": "Permiso para eliminar tipos de vehículos"},
            {"code":"vehiculos:view", "description": "Permiso para acceder a vehículos"},
            {"code":"vehiculos:read", "description": "Permiso para leer vehículos"},
            {"code":"vehiculos:write", "description": "Permiso para escribir vehículos"},
            {"code":"vehiculos:delete", "description": "Permiso para eliminar vehículos"},
        ]
        
        for d in defaults:
            await cls.get_or_create(defaults={"description": d["description"]}, code=d["code"])
            #                        ↑ campos a setear si crea        ↑ campo de búsqueda