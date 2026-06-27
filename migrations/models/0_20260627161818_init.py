from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "roles" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" VARCHAR(255),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_roles_name_3e8175" ON "roles" ("name");
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password_hash" VARCHAR(128) NOT NULL,
    "is_active" INT NOT NULL DEFAULT 1,
    "must_change_password" INT NOT NULL DEFAULT 1,
    "password_changed_at" TIMESTAMP,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
CREATE TABLE IF NOT EXISTS "permissions" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "code" VARCHAR(100) NOT NULL UNIQUE,
    "description" VARCHAR(255),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_permissions_code_8330fb" ON "permissions" ("code");
CREATE TABLE IF NOT EXISTS "bienes" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "tipo" VARCHAR(100) NOT NULL,
    "descripcion" VARCHAR(255),
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_bienes_tipo_73abb3" ON "bienes" ("tipo");
CREATE INDEX IF NOT EXISTS "idx_bienes_tipo_e839c9" ON "bienes" ("tipo", "descripcion");
CREATE INDEX IF NOT EXISTS "idx_bienes_is_acti_af48b2" ON "bienes" ("is_active");
CREATE TABLE IF NOT EXISTS "trasteos" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "fecha_ingreso" TIMESTAMP NOT NULL,
    "fecha_salida" TIMESTAMP,
    "is_autorizado" INT NOT NULL DEFAULT 0,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "usuario_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
) /* Modelo para registrar trasteos (traslados\/movimientos) de bienes de un usuario */;
CREATE INDEX IF NOT EXISTS "idx_trasteos_usuario_d92294" ON "trasteos" ("usuario_id", "is_active");
CREATE INDEX IF NOT EXISTS "idx_trasteos_fecha_i_986c62" ON "trasteos" ("fecha_ingreso", "fecha_salida");
CREATE INDEX IF NOT EXISTS "idx_trasteos_is_auto_36c43c" ON "trasteos" ("is_autorizado");
CREATE TABLE IF NOT EXISTS "trasteo_bienes" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "cantidad" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "bien_id" INT NOT NULL REFERENCES "bienes" ("id") ON DELETE CASCADE,
    "trasteo_id" INT NOT NULL REFERENCES "trasteos" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_trasteo_bie_trasteo_5e8b11" UNIQUE ("trasteo_id", "bien_id")
) /* Modelo intermedio para asociar bienes a trasteos con cantidad */;
CREATE INDEX IF NOT EXISTS "idx_trasteo_bie_trasteo_8e0434" ON "trasteo_bienes" ("trasteo_id");
CREATE INDEX IF NOT EXISTS "idx_trasteo_bie_bien_id_735c9a" ON "trasteo_bienes" ("bien_id");
CREATE TABLE IF NOT EXISTS "parking_spots" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "code" VARCHAR(20) NOT NULL UNIQUE,
    "vehicle_type_id" INT NOT NULL,
    "is_parking_public" INT NOT NULL DEFAULT 0,
    "is_active" INT NOT NULL DEFAULT 1,
    "monthly_price" VARCHAR(20) NOT NULL,
    "minute_price" VARCHAR(20) NOT NULL,
    "parking_status" VARCHAR(10) NOT NULL DEFAULT 'disponible' /* AVIABLE: disponible\nBUSY: ocupado */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_parking_spo_code_3bf736" ON "parking_spots" ("code");
CREATE TABLE IF NOT EXISTS "horizontal_properties" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "nombre" VARCHAR(150) NOT NULL,
    "direccion" VARCHAR(200) NOT NULL,
    "telefono" VARCHAR(20),
    "localidad" VARCHAR(100),
    "barrio" VARCHAR(100),
    "correo" VARCHAR(150),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_horizontal__nombre_bf4a19" ON "horizontal_properties" ("nombre");
CREATE INDEX IF NOT EXISTS "idx_horizontal__correo_2dada9" ON "horizontal_properties" ("correo");
CREATE TABLE IF NOT EXISTS "ph_torres_interiores" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "t_numero_letra" VARCHAR(20) NOT NULL UNIQUE,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_ph_torres_i_t_numer_14cc48" ON "ph_torres_interiores" ("t_numero_letra");
CREATE INDEX IF NOT EXISTS "idx_ph_torres_i_is_acti_b04d55" ON "ph_torres_interiores" ("is_active");
CREATE TABLE IF NOT EXISTS "ph_casas_apartamentos" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "c_numero_letra" VARCHAR(20) NOT NULL UNIQUE,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_ph_casas_ap_c_numer_1e3600" ON "ph_casas_apartamentos" ("c_numero_letra");
CREATE INDEX IF NOT EXISTS "idx_ph_casas_ap_is_acti_52ce69" ON "ph_casas_apartamentos" ("is_active");
CREATE TABLE IF NOT EXISTS "ph_casa_interior_links" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(12) NOT NULL DEFAULT 'deshabitado' /* EN_PROPIEDAD: en_propiedad\nEN_ARRIENDO: en_arriendo\nDESHABITADO: deshabitado */,
    "num_habitaciones" INT NOT NULL DEFAULT 2,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "casa_apartamento_id" INT NOT NULL REFERENCES "ph_casas_apartamentos" ("id") ON DELETE CASCADE,
    "torre_interior_id" INT NOT NULL REFERENCES "ph_torres_interiores" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_ph_casa_int_casa_ap_22e670" UNIQUE ("casa_apartamento_id", "torre_interior_id")
);
CREATE INDEX IF NOT EXISTS "idx_ph_casa_int_casa_ap_22e670" ON "ph_casa_interior_links" ("casa_apartamento_id", "torre_interior_id");
CREATE INDEX IF NOT EXISTS "idx_ph_casa_int_status_b937eb" ON "ph_casa_interior_links" ("status");
CREATE INDEX IF NOT EXISTS "idx_ph_casa_int_is_acti_6f096b" ON "ph_casa_interior_links" ("is_active");
CREATE TABLE IF NOT EXISTS "parking_visitor_reservations" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "visitor_type_document" VARCHAR(3) NOT NULL,
    "visitor_document_number" VARCHAR(12) NOT NULL,
    "visitor_name" VARCHAR(100) NOT NULL,
    "visitor_email" VARCHAR(100) NOT NULL,
    "visitor_cell" VARCHAR(25) NOT NULL,
    "vehicle_type_id" INT NOT NULL,
    "vehicle_code" VARCHAR(20) NOT NULL,
    "qr_token" VARCHAR(64) NOT NULL UNIQUE,
    "qr_generated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "starts_at" TIMESTAMP NOT NULL,
    "ends_at" TIMESTAMP NOT NULL,
    "billed_minutes" INT NOT NULL,
    "total_price" VARCHAR(40) NOT NULL,
    "status" VARCHAR(10) NOT NULL DEFAULT 'activa' /* ACTIVE: activa\nCOMPLETED: completada\nCANCELLED: cancelada\nFINISHED: finalizada\nVIOLATED: incumplida */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "casa_interior_torre_link_id" INT NOT NULL REFERENCES "ph_casa_interior_links" ("id") ON DELETE CASCADE,
    "spot_id" INT NOT NULL REFERENCES "parking_spots" ("id") ON DELETE CASCADE
) /* Modelo para reservas de parqueadero de visitantes. */;
CREATE INDEX IF NOT EXISTS "idx_parking_vis_spot_id_9960b0" ON "parking_visitor_reservations" ("spot_id", "starts_at", "ends_at");
CREATE TABLE IF NOT EXISTS "personas" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "nombres" VARCHAR(120) NOT NULL,
    "apellidos" VARCHAR(120) NOT NULL,
    "edad" INT NOT NULL,
    "celular" VARCHAR(20),
    "email" VARCHAR(150),
    "is_propietario" INT NOT NULL DEFAULT 0,
    "is_arrendatario" INT NOT NULL DEFAULT 0,
    "acepta_terminosycondiciones" INT NOT NULL DEFAULT 0,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "casa_interior_link_id" INT NOT NULL REFERENCES "ph_casa_interior_links" ("id") ON DELETE CASCADE,
    "usuario_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_personas_nombres_7d1ab1" ON "personas" ("nombres");
CREATE INDEX IF NOT EXISTS "idx_personas_apellid_57681c" ON "personas" ("apellidos");
CREATE INDEX IF NOT EXISTS "idx_personas_email_8e3574" ON "personas" ("email");
CREATE INDEX IF NOT EXISTS "idx_personas_casa_in_4386b0" ON "personas" ("casa_interior_link_id", "is_active");
CREATE INDEX IF NOT EXISTS "idx_personas_is_prop_71461d" ON "personas" ("is_propietario", "is_arrendatario");
CREATE INDEX IF NOT EXISTS "idx_personas_nombres_c39d0e" ON "personas" ("nombres", "apellidos");
CREATE TABLE IF NOT EXISTS "parking_monthly_assignments" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "vehicle_type_id" INT NOT NULL,
    "start_date" DATE NOT NULL,
    "months" INT NOT NULL,
    "end_date" DATE NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* ACTIVE: active\nCANCELLED: cancelled\nEXPIRED: expired */,
    "monthly_price" VARCHAR(10) NOT NULL,
    "total_price" VARCHAR(12) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "persona_id" INT NOT NULL REFERENCES "personas" ("id") ON DELETE CASCADE,
    "spot_id" INT NOT NULL REFERENCES "parking_spots" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_parking_mon_spot_id_e8eb43" ON "parking_monthly_assignments" ("spot_id", "start_date", "end_date");
CREATE TABLE IF NOT EXISTS "parking_lottery_config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "weight_propietario" VARCHAR(40) NOT NULL DEFAULT 2 /* Peso adicional para residentes propietarios (vs arrendatarios) */,
    "weight_good_social_behavior" VARCHAR(40) NOT NULL DEFAULT 1.5 /* Peso adicional para residentes sin llamados de atención */,
    "weight_payment_compliance" VARCHAR(40) NOT NULL DEFAULT 2 /* Peso adicional para residentes al día en pagos */,
    "max_consecutive_months" INT NOT NULL DEFAULT 6 /* Máximo de meses consecutivos con parqueadero antes de exclusión */,
    "exclusion_draws" INT NOT NULL DEFAULT 2 /* Número de sorteos que el residente debe esperar antes de participar de nuevo */,
    "assignment_duration_months" INT NOT NULL DEFAULT 1 /* Duración en meses de cada asignación de parqueadero */,
    "is_active" INT NOT NULL DEFAULT 1 /* Indica si el sistema de lottery está activo */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    "propiedad_horizontal_id" INT REFERENCES "horizontal_properties" ("id") ON DELETE SET NULL /* Propiedad horizontal a la que aplica esta configuración */
) /* Configuración global del sistema de sorteo de parqueaderos. */;
CREATE INDEX IF NOT EXISTS "idx_parking_lot_propied_47521b" ON "parking_lottery_config" ("propiedad_horizontal_id", "is_active");
CREATE TABLE IF NOT EXISTS "parking_lottery_rounds" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "round_number" INT NOT NULL /* Número secuencial de la ronda (año*100 + mes) */,
    "round_date" DATE NOT NULL /* Fecha en que se ejecutó el sorteo */,
    "start_date" DATE NOT NULL /* Fecha de inicio del período de asignación */,
    "end_date" DATE NOT NULL /* Fecha de fin del período de asignación */,
    "status" VARCHAR(11) NOT NULL DEFAULT 'pending' /* Estado actual del sorteo */,
    "available_spots" INT NOT NULL DEFAULT 0 /* Número de parqueaderos disponibles en este sorteo */,
    "assigned_spots" INT NOT NULL DEFAULT 0 /* Número de parqueaderos asignados en este sorteo */,
    "notes" TEXT /* Notas adicionales del administrador */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "config_id" INT REFERENCES "parking_lottery_config" ("id") ON DELETE SET NULL /* Configuración usada para este sorteo */,
    "executed_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    CONSTRAINT "uid_parking_lot_round_n_c64cd0" UNIQUE ("round_number", "config_id")
) /* Representa una ronda de sorteo de parqueaderos. */;
CREATE INDEX IF NOT EXISTS "idx_parking_lot_round_d_8fca6d" ON "parking_lottery_rounds" ("round_date", "status");
CREATE INDEX IF NOT EXISTS "idx_parking_lot_config__82626a" ON "parking_lottery_rounds" ("config_id");
CREATE TABLE IF NOT EXISTS "parking_lottery_participants" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'eligible' /* ELIGIBLE: eligible\nEXCLUDED_TEMPORARILY: excluded_temporarily\nEXCLUDED_THIS_ROUND: excluded_this_round\nSELECTED: selected\nNOT_SELECTED: not_selected\nWAITING_LIST: waiting_list */,
    "base_score" VARCHAR(40) NOT NULL DEFAULT 1 /* Puntuación base del participante */,
    "propietario_factor" VARCHAR(40) NOT NULL DEFAULT 1 /* Factor por ser propietario (1.0 = arrendatario) */,
    "social_behavior_factor" VARCHAR(40) NOT NULL DEFAULT 1 /* Factor por buen comportamiento social */,
    "payment_compliance_factor" VARCHAR(40) NOT NULL DEFAULT 1 /* Factor por cumplimiento de pagos */,
    "final_score" VARCHAR(40) NOT NULL DEFAULT 1 /* Puntuación final calculada para el sorteo */,
    "waiting_list_position" INT /* Posición en lista de espera si no fue seleccionado */,
    "random_seed" REAL NOT NULL /* Semilla aleatoria para desempates */,
    "notes" TEXT /* Notas adicionales sobre el participante */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "assigned_spot_id" INT REFERENCES "parking_spots" ("id") ON DELETE SET NULL,
    "persona_id" INT NOT NULL REFERENCES "personas" ("id") ON DELETE CASCADE,
    "round_id" INT NOT NULL REFERENCES "parking_lottery_rounds" ("id") ON DELETE CASCADE,
    "user_id" INT REFERENCES "users" ("id") ON DELETE SET NULL,
    CONSTRAINT "uid_parking_lot_round_i_50caf6" UNIQUE ("round_id", "persona_id")
) /* Participante en una ronda específica del sorteo. */;
CREATE INDEX IF NOT EXISTS "idx_parking_lot_round_i_7b117b" ON "parking_lottery_participants" ("round_id", "status");
CREATE INDEX IF NOT EXISTS "idx_parking_lot_persona_0118b5" ON "parking_lottery_participants" ("persona_id", "round_id");
CREATE INDEX IF NOT EXISTS "idx_parking_lot_final_s_8e25c1" ON "parking_lottery_participants" ("final_score");
CREATE TABLE IF NOT EXISTS "resident_behaviors" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "total_warnings" INT NOT NULL DEFAULT 0 /* Total de llamados de atención recibidos */,
    "warnings_leve" INT NOT NULL DEFAULT 0 /* Llamados de atención leves */,
    "warnings_moderado" INT NOT NULL DEFAULT 0 /* Llamados de atención moderados */,
    "warnings_grave" INT NOT NULL DEFAULT 0 /* Llamados de atención graves */,
    "months_payment_current" INT NOT NULL DEFAULT 0 /* Meses al día en pagos (últimos 12 meses) */,
    "is_payment_compliant" INT NOT NULL DEFAULT 1 /* Indica si el residente está al día en pagos */,
    "consecutive_months_with_parking" INT NOT NULL DEFAULT 0 /* Meses consecutivos con asignación de parqueadero */,
    "total_months_with_parking" INT NOT NULL DEFAULT 0 /* Total de meses con asignación de parqueadero */,
    "pending_exclusion_draws" INT NOT NULL DEFAULT 0 /* Número de sorteos que debe esperar antes de participar */,
    "neighbor_complaints" INT NOT NULL DEFAULT 0 /* Número de quejas de vecinos */,
    "incidents" INT NOT NULL DEFAULT 0 /* Número de incidentes registrados */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "persona_id" INT NOT NULL REFERENCES "personas" ("id") ON DELETE CASCADE
) /* Registro del comportamiento de cada residente. */;
CREATE INDEX IF NOT EXISTS "idx_resident_be_persona_009e42" ON "resident_behaviors" ("persona_id");
CREATE TABLE IF NOT EXISTS "warning_records" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "warning_type" VARCHAR(8) NOT NULL /* LEVE: leve\nMODERADO: moderado\nGRAVE: grave */,
    "description" TEXT NOT NULL /* Descripción del llamado de atención */,
    "incident_date" DATE NOT NULL,
    "is_active" INT NOT NULL DEFAULT 1 /* Indica si el registro está activo */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "persona_id" INT NOT NULL REFERENCES "personas" ("id") ON DELETE CASCADE,
    "recorded_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
) /* Registro individual de cada llamado de atención. */;
CREATE INDEX IF NOT EXISTS "idx_warning_rec_persona_2b8ede" ON "warning_records" ("persona_id", "incident_date");
CREATE INDEX IF NOT EXISTS "idx_warning_rec_is_acti_7aa0ba" ON "warning_records" ("is_active");
CREATE TABLE IF NOT EXISTS "vehicle_types" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "emoji" VARCHAR(10),
    "description" VARCHAR(255),
    "display_order" INT NOT NULL DEFAULT 0,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) /* Modelo administrativo para gestionar los tipos de vehículo. */;
CREATE INDEX IF NOT EXISTS "idx_vehicle_typ_is_acti_6e42ef" ON "vehicle_types" ("is_active", "display_order");
CREATE TABLE IF NOT EXISTS "vehicles" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "placa_code" VARCHAR(20) NOT NULL UNIQUE,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "persona_id" INT NOT NULL REFERENCES "personas" ("id") ON DELETE CASCADE,
    "vehicle_type_id" INT NOT NULL REFERENCES "vehicle_types" ("id") ON DELETE CASCADE
) /* Modelo para gestionar los vehículos de las personas. */;
CREATE INDEX IF NOT EXISTS "idx_vehicles_placa_c_94246f" ON "vehicles" ("placa_code");
CREATE INDEX IF NOT EXISTS "idx_vehicles_persona_e622dc" ON "vehicles" ("persona_id", "is_active");
CREATE INDEX IF NOT EXISTS "idx_vehicles_vehicle_f60996" ON "vehicles" ("vehicle_type_id", "is_active");
CREATE TABLE IF NOT EXISTS "domain_config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "domain" VARCHAR(255) NOT NULL UNIQUE,
    "is_active" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_domain_conf_is_acti_b3b810" ON "domain_config" ("is_active");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "permissions_roles" (
    "permissions_id" INT NOT NULL REFERENCES "permissions" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_permissions_permiss_96cfa0" ON "permissions_roles" ("permissions_id", "role_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztXVtz20ay/isoPsm7ildSLK+jqvNAS3TMXd0ORTvZtVKoITAiJwYBBhfZ2j3576d7Bi"
    "DuIECCBEDOS2IB00Pg68FM3/u/vbmlU8N5/cmhdu9C+W/PJHMK/4hdP1Z6ZLEIr+IFl0wM"
    "PtCDEfwKmTiuTTQXLj4Rw6FwSaeOZrOFyywTrpqeYeBFS4OBzJyGlzyT/eFR1bWm1J3xB/"
    "nyG1xmpk6/Uyf4c/FVfWLU0GPPyXT8bX5ddV8W/NrQdD/wgfhrE1WzDG9uhoMXL+7MMpej"
    "meni1Sk1qU1citO7toePj0/nv2bwRuJJwyHiESM0On0inuFGXrckBpplIn7wNA5/wSn+yg"
    "9np2/+/ubdj2/fvIMh/EmWV/7+p3i98N0FIUfgdtz7k98nLhEjOIwhbsg2/u8UepczYmfD"
    "F6VJgAiPngQxgKxRFOfku2pQc+rO4M/zkwLIPvdHlx/7o6Pzk1f4JhYsZbHAb/07Z/wWoh"
    "qiuCCO882ydXVGnFkVKFOE9eAZXAgBDT/FbSB6evauBKQwKhdTfi8OKnNU2EbYc8bafG9Z"
    "BiVmztcdpUvgOQHCbQG6XLNrAVqA3/u7u2t86Lnj/GHwC8NxAsdPN+8HADCHFwYxl0Y//8"
    "h27jmuqs2IOaVqsPYqwps3hUQ6e0sQUOkqcdNAXwEwLpvTFZtDfIoE0Lo/x+vgHyVQ9wHc"
    "4X5RAPp4eDN4GPdv7mPIX/XHA7xzxq++JK4evU3sJMtJlF+G448K/qn8++52wAGzHHdq81"
    "8Mx43/3cNnIp5rqab1TSV69LWDy8GlGGs1myK0a3A0TlkDI5vY+eEd9DvTePHXUUc46y/5"
    "QsZ6C31NxsYpJWMbZaz/8CFfbTjO1EoaQoRitZrQEvbVoCmgevX0NVNRQETSAH6wbMqm5j"
    "/pC8dxCE9ETC1L8vIVyZE/Tfvw+zNYA8HVcG3Z5NtS5YwuDXg9eCkqRIDL/sNl/2rQ4yBO"
    "iPb1G4GjOwdN+AXHpZaTIXv5lB/+OaIG4S+RC+ZYzNItPONSErUdyyQb4nAvZmmz4FMMg2"
    "G5LrVfcNQTmzqqLydshsq1mPSSz9l9bGzLM3VHhUfRvLqwGeGc3YdmQWyXaWzBX3rDb8lH"
    "5j6YstRx11J84J1NmMRRbaqBHrXpovlFTDfik3ULFTyTrDMrchbFTqn0rfnZPHmFmGTKnx"
    "p/G38peqRn2IyDoz7fZoxHqbQZd85mXNVeLG3F0U0p+lgVQEyQrYXl7jekOJhn5+cl0IRR"
    "uXDye3E8pTVmL5R2aY3ZU8Yu5Y+YKlxGSV66lNcX2QK/dfv4uy1RLaZbz5njZKsEN8R8GV"
    "v435KGm/vlbG08tAuMN/z51YRsGn8bG9cR7BdRW5fAzLI56F/pSwJR3wK0ZIs/ImIccmeg"
    "sU5nSbrl3JnGI7iuJqXJPwul78ibZMjg8ffMl8QTa2Wr8vgXYJ5Oe79JubxmuZzDWkGkDM"
    "Z3US4/PSkjmMOo/IiDEymaS9FcSnBSND9YxlYVzWsTTUMBazOhdF1vYtvE0eA9koJoUoSP"
    "i6MRYTMph6Yl1VrEUbETFMqj7xnNlET59UIZdAIjdmAO/tJz2YL7TP05NZwTBn2JRA5K4b"
    "Ru4TQAvaxQFYzfVkBsZ6VTbT3pVJPSqYwv3nrUq5T490IwlBL/njJ2fWN8rRFrgTDYPk43"
    "EkERxPFliM2REL98yTnKm5Wyc+8GJ7CUBbGJYtMpw/G2EsyhHOG/DKJbzt/m1jObA6tcy3"
    "ml6FQREjr+yzMVz/GIzYQgHYF1C9OXken94b6yExHkUa5/otqMqPB88NkIIZRfcIjBdBKK"
    "/vCZ2Ow/8GhS/K9d/E+zoMIRkiLu5inSkVOjVA5M7Atai50hrUxoapiZ8c0vfcCv0oZitD"
    "vUiKoahxpRiaSaKdVMqY30pJp5QIxNReLHxfOS4nOcSObhRZFMw1g5Fa97sXHHiVS8+AJZ"
    "Pxsv9DxJy0ZvG5aNPKdgArSVFg61go8wMETAm1J7TnXm2ySIY2mM2IG1gYSmCYBG0Yjpgl"
    "qi55k11p8tw4rxJXgv7sJFEH5LOyv9N4c1zg0VOIz/IU0Ua2ysxwUmiiizSqIXJdnd+XTa"
    "NIZSEN8zeU0K4nvK2JQgHhwf5fe4CMUhieBR0CJncHnc4kSHBF2B9hKRdzbUXjpZ++I4oc"
    "DE10i2ApP8emvArntKShK4yKZUVe3bprpzT+yv8HoPC8vtZWXjRG4fF6bjiIGqAyNlgnz3"
    "NIkDSsQ5KxPpeJYf6HiWinN8pjMGw/hU1Y7cDMpDOncTXqdgE1l4E4Np1b1PaXrp2pOuva"
    "1XqLVMd2a8qAubaZU20RRhN0sp17+fzpnpuXQNQBN0Es+gsq8vnLnE9TK8BojowPTmKWE8"
    "Udw3Ocvu8O3pDCRLk01E1lHCbt7/POy/vx5cKOGoR/P9p4d/XSiW5i38MI/qKRGlMiIKEi"
    "Jkdulemqik7XFPGbt+rDlxHDY159R0N3TK3giZoL+cr50sz3XNxtQi5jDXslVgB7Wf6yj1"
    "+FnMOAon7DA8QS3M2tZO1wthbtPOlf6uMqxdmR/faptXIMcnGLnlnGC0tPkmA5DIbFfFQw"
    "L/oqYu/i0d7nWbyaShpwZDT3y1poWlbADjVEWCUjtRLIAIBZ0sm0LGcZC7vkKCQ11Wy22v"
    "wqKK0uz7ktpM+W9E6Q9NjkmF/3I8/Az6vhjwaF72by8H19eDqwsMYNOoYVD90Rz8ej8c4T"
    "X6fcFsmoqQK2ME+KmEDeCnXBPATynL1oHbCuu3qbiWS4zqeCbIOormWRk0zwpa2EkL1V4a"
    "MqSFak8Zm9eOppoyEic6VIExokCXxC1CcUigFUTHOX5g0IbhXYkwo/bBWDbKK7JCVsfGLc"
    "ImUJviV7qdVIuxi+9KbQqSyzA7Z1gPs43Tq82HeWbyqnVRODUvRgIXgLlEp7aFf/IfIKZL"
    "nddJFWiNKR5N0LfIHI4xBcRnEw3NBnUuHs0fFFz9FzDNE7Up3CAKMZSFRx3XSk55FPniXy"
    "GpRhysl+FSmwEUAIdNVYOZX3E6g2js0Ts5efrRVIhyCSP72D+KoKXVGvo0YyRRjuAXeMbT"
    "FN6Hz6L8VSHhaP5bAeB/uVBAbLHwfY3wDZUjAMjjo48V05pPbECezgmDpQ2apWcQm8/CDV"
    "IOiEXK3xSKfb4IvDusYXxSqls6f2djiSqSTBgqpqoIU3AuFP4PC3OwnoDPnk1sHBVRTWBC"
    "m2rMEtcAJEPzsBKN//ugkYNyC/+AH8MJYEjsN5UjoSgfK0sFGV7F1V5zcWUdI7Pji4H+C0"
    "sTc/0mZn9xckNxsBKraLa5E3RTx/2xhIr7Y66G+2MqVNNHJwBGNb35RGQVVwU4Y4puQly/"
    "GSGAqGrfrSRdR/HcRi3VABp+Eq2D6ZJQgpoCFS3G62Aa0HUT0rNyJWoLKtTKQPgt2CUCKK"
    "rmZCTpOrooa49+/QP1ia9ZaWj5WEZpupjj8vZNCRTfvslFEW+lUFy+8hpW5AxyaUpumY8g"
    "puFVYW6MsJts7Qgbg9cu5GOgnFfkYoRM8rBpHsZNRRUEqTThocpRhZEBV1Rjc2KsExygC9"
    "LX/hTtBLMoNmhwObzpX4PafnyWSG4LJIM3KSGqq9FD3CdSFD1EHs3Lu5v768GYRw9Z84VB"
    "XaKTjKAifvXD8Hb48BEvPjGTGFhEFq5+Ht5d9/kMzNQ8mMMvFNx8fIyM6NhTaU1GdOwFY1"
    "MRHXmesGr2lBWzHKpMIGM+ZMxHozEfed9lDYAWOca7jfCKzaxNoSL3trVgVCf6R2wwYJmg"
    "SPSy6iplDDsuChaZLceBXmItqO2ynXSeFAEQopCrhsDLVjP1+/x9kFPY5dunQ4pudps8L6"
    "XnnBcoOufpbpPMplrlXpNRoq56TMq5TIp8Jum0CthQnyyzWgPUCE03m3bW7nsyLI03DcrY"
    "GPNxjBF1EsitOOsnxM5sI5APZEghUQwr/fFDvAKKIcWWUOzeUSONanthe5FGtT1l7PqFfI"
    "KiLIDME5vWU5Dlks+1ywOnt9QvlVBxVAiGhmOAPFkYTCM8clwRL+rZYYx9Ob9FI1VcgjyX"
    "LI06TIEpSLkQg3ahOMdtFhFrRaLTK5Yt5cxygyZJOABOXBPVRbzEhwmFTzz4ghogHlqO1M"
    "S3pInn+DmLVPGtOje3KyCV0npOC9Se07TeE67RCkjGiCSWy3Ceah1+6M67+7Thk47I5iJH"
    "q5KGE5J0UlGs325ROctgs+yCfdQR0wd7QpBcVcw8TiwrmacrmUelpMr4JqklwIkjXKMLkJ"
    "KweSAzLecFHkJnaCnP7DtZBPaKmSTwska/bL8t7TrSYHe4jF0RBbdp/JuMfGusn3kDutF2"
    "w9/SKysNqIzdyondWhm1lbFka4C3ZOP49tRCT6JY0Df+YTBWbj9dX5drHB8UHZINCwoq8i"
    "+CCvo1tCxYqyh/WwGa0Bl5ZrxWlWbZ+obQjKjDdFgx7/1ZOwwMvLKJn1UtuPwiJhvxuToM"
    "il+QYNOeH2KWjuGwTS8olwoCEaGX4QuNDzgu9IjORDy1szyjdxJWzIsmUdtS4RSzydITGj"
    "hGpV9zLWk/36+ZwDuFYUFQZ4qyi/Uw6veQSCudtNJJY05PWukOiLEbhNWB3u+oaAvYUBrc"
    "H0PJVkXEBExZQmJyyCoxkTNPjdTS3UkUnZQTdyonamvLiWlKKSdKOVHKiVKckHLioTF2Uz"
    "kxboqSwuJuhcU4TKslxxSsK8XIuD9wC3Kkn34REVZ9z5moHbH8ebj4W3bmRilSlEb90mZS"
    "Mt2yZNrBAnSA5IxMGLbn6KWA7Q1u1fvR3f1wcNXHFpWmH/CrE+xceav2R6Ph4Pbqjt/CPG"
    "ZqYt+Pq8HDxz5ITn28k/yBxuv+Ax9U8UR5gaK5Sz2LdHexOmdNL3ypMEiFQcqVUmE4TMZm"
    "h3+mZbAqwZ9p6kMN/UxLruWhzKQ9JCALIkHj2KRBrRymmIrbaB+kZQMWM9dNyfKIJO6VqD"
    "e0ttuw5uxsVSsgpjsgJZtPbhCvldkGszuQx9ZjtGDE+pB0sj3rVk1O8cooGTamVOmU1X1U"
    "46VbShmVepep6ifK1LAmvJGmoTjMcemcYFNNx7JdmmxjmtFPddMJsbvq2NItRzGwwSoR7U"
    "RP59SFu0BkKlRn/NWxbakj2n1OiENxJtHNlPdyXWCypcvsR5P87sGPAi0zFUCPPTGN2Iom"
    "nk5nU4u/RBln7NJAoUaqkaaKmkjL11riWr7l6xucdzO3OJm8sJ1F9gTNdLU4e32S/grvqW"
    "MpROQEY8tgvxkxDw6n2GZ4+eCOcvTsKNHUbedVOdNXAQuChhjnFfph+JhOLUtXHUtj8CVM"
    "ImHs1bmTN1MzbDp9fV6ZTbjBwK/Oic5bKivwSOZ6RaVqZtKCvPA+rby5BwukxTU+oMx5uv"
    "Md4SEkulMThZpweypieHbOF7RC4y9QzcMzQ51jDlEVY3H+BLtTTd+m8b8Rh/V3NucH+xxE"
    "YEcJn9Pif8T6oPOW6jiWftcMz6n2tdRtJ/CfAZUJUDqq8CODsknbfe+W40jmfvd6IWs5vP"
    "YdSGHLTwLuTeCKA8ISiERLXizTv2z8y/Toc1n3Ss0MCZP0VB1ESny76t9K8SS7Y9Npmk1X"
    "MTkZtiTxxQDoGoE9iuCDRwbEZeVmWLIX3hlYLDoWgHSYEldKfBUKK0OKrUz0yCqJtfTlSJ"
    "O/9OUcOmPTvhz/s5u8VPTiJOkOqP5EzAaZb3YpiWTBDM1iuoM6xVv2AWVBW4PTIqc/0B7x"
    "pazHo2Dt5pTByN57amBK56uIpHbUDQqJ2JZnblrowDfyj3CqnS7vDCu956DKwU0msK4DnX"
    "GztbwLF4oAL9+DsgS3vAMlZO1qB8qILtB1CF+l4plEsS1Tr+QvqUiP7pFLZNQcDY6gJ8KK"
    "5oSopQfkuEU5sKx5XyfCHSkRK9g3ZsIqcx5Nzmvfy7L8BUVnzsIyGTpY8hwjX8Tix4Snid"
    "gRfJdTOpZYDETJk6s1kVhhQbKMQJYekxo9Jkn2lEQwSdZwmEvMioUmRDSnc0cinsNiqR8R"
    "PubU+svpyYnyV/wsSvpD6pZS4ys9rb0VQR5QFWluu4X+A9Vm3Egu9hKF/o4mXHFWcJtJ9d"
    "Mh03gO2lm60brtVsYxTtU2HGHFMhO9EtwJvqDCqa1bOt/gE2a+bYBK11iatMULE1B7YmZT"
    "aHYwFWMB3EQA0oAOHEyfQDunFwRpVPi2EwkVp2USKk7zEypOU300ngnjb65il+FKZv805e"
    "7OswzfZMIlkydz4Z5bWf7ejt8FFKXKoKcIW4u52CfQVd8GxE3LzcoWGtPveelCAUGzDTt6"
    "t5ZLnNDnzr1XBvw9hwMPAdNFFMdGW/B48Os4ZuoNdoyjm/6vr2Lm3uu725+D4ZEd5vL67r"
    "10o+yjtV26UfaUsWk3ytJgUP48itE0bOqv2eZWf/ALanhruKnShAfkpyrwjIRh2Bua3Zvr"
    "orkjM/Fx0kwf/WpLODkiK1B6ObI+yM3qpQd1uw+9EPgOnBlRcPJdGgkIyzs2ksxc7d6I/B"
    "RFRSn0UWDUoCYsL5hREbEcpJ0ca82Cro6+MScaNbnjlZlPlj2PhcNFQhmPFcdTFp7pepER"
    "GjE0z4AN69F06FQogyaaLzlWFgbWT8iEGeIBHHhG61h58UMkYS0R3Uq+V4E7xD/8RK5Tdm"
    "mV6MCoMyRCdKyEo/i9JwZ6leposI9JV4ksqwL7u8GmaCvKMuZdD38evr8eXCjBoEdz8Ovl"
    "9aerwZU6Htzc3436o+H1vy5EvLUOh4RL5wsQ521mvETHfhw+qKO7T7dX0aEz5gjn6KP5ML"
    "geXI4HcJt7GuEVH83bu7EaXjctVw3v/dIfjoe3P6vXw4fxhfKNMJdvTMxx1zE01l+mEFPI"
    "/I8srTUW5UbECZvKVslKhkhshn6SnKFETgG6uXncT394d/ymdPpDJJ9JfYLjp3LKUPYELc"
    "L+A38oBT4s+DzsaAKXcgQEyv/EUriayeBK5Fqtx4n8SdrJjYkH4gfmL1mYQc4whVwR79AI"
    "D9IZVWt+EEXztJMTmoeP6rOAG+ebysaKCljVYE9Qtgjo5ObPnzSUh30Fvj4/vg/76UmFYy"
    "AqBKgLy2GB/lhSis2lbzqmFx4lltWDD8h91iLTCtNOTEt5ikVpla5gV3fYCjF1aw6CGs1Q"
    "ID4YFsmLFYrTJSB/QsLdBgY80DmDeRViUAJ7DPPXOIwCAZf4zrLNFvndJxCtlfsRLPaH4d"
    "1t3EDOb8aX/mjQv95fP59jTWyeTlirPCl9fdIlJH19B8bYlK8vFkdSzR2VRXpADqmM4k0V"
    "c6ViRIdU6S4dzVsJuJgR+EBh8xxasb5ihOKAvtICt7Ed5KvU4zUum1vUIkfbccKfGf2wVl"
    "dQXIS15jbNQexi1bokePHtvEzP8ayUkcNzokf2pRIRCDGho46lJxy3D/5snUUxSxirHIyw"
    "Tb97qgV3htc9q013vs898EgvbeKlEwmnGDArHM4JC3VQEGbp7c7KI6xCzn3rmjf3svzqM+"
    "b4mT42L5KCev7Fo/mDcp1X3Ew5ctnCUl7gZ0yX6UR/hcM/wjxoiDGW5l28+r8e/Z1gQqLG"
    "JjDUyXGqp1znSb+69ILX6AV3Lcwq95u4Vwn4TxM2GvA/xsfhCYK5S9VfeGV9DXVLyAFUqk"
    "GzaigVGLsTdI3inL8T4OM1DS3uyrZvUa8Kb5S2pRAHj9g0zFObrLeEl4QtBZg/X0Poisp0"
    "YalND+MEMkTK/NKQuRM0ivYNr2yXVYFTORKBeYbL5vDX6ZmogtdQGjdzUmVOM9BfVeouc4"
    "p2Vb0Li0BGit1to0BqnaXvUiVP1W/Mnal+nGuFr6TETC34XFKlU9tYEVKIgJuxo3COdkiU"
    "y2K2rWSCn9+trl/CtmCGNuXwRkvZrqpe2wwrTCyWPbFssfmLnynPhhzqNrHgD6HBw7+eQZ"
    "cym5JDGUhseIBVQTdG0yZMgwejaBmZ+pnTDQEroyX2wqkuoyX2lLF5TZqkn3/zaqbSeVjV"
    "ediM3+YXYUsaUc2yM6s/xgccF3lsfLuUavOxVd01wCX2zHRRPEn4WXzjc8qwVOC1qTILOm"
    "/ueXsr0EpQ7IXlpXjCbxP4W0BpMXxig+uOUYdQbmHHIqfLcSg9ibJgv8mO79t1ygTrkqOQ"
    "QrBcgmJyjt2lKWaHEV8PPg8uuJPg0by5uxqMeB/3wKL9aP486uOApYW4amLguxJ5ge9y0w"
    "LfJVMUok+f4kB+0HaCrGnQr8Sf8czpvO1lY3vfViK441tPpvRarPG1r5Rh1dM6MyUhXZxw"
    "Dxu02MEpKduySOVKas2SsVJrbjg6nmtKa9QKSxPKoO/IspJ2h/WCliPLqgYIOx+7nP7KWh"
    "Vz+5nOGOz2Y4F6ynITvX1cZLd5FgP9b+24jNXmRtR9CsvTohQpEoWnIFxiaqvNDSYYz+q7"
    "uGYiIkLzjIzKVptO+Gg++LXhicH+w7sJ8eHPxIBlK4rpUtDylQgqyhFe1a05LIFXpU05Mf"
    "keC04b5EXFZWJL003tphv+/xRyaLLJ8fr64xu2FJTHL172/aRMOSYYlV/4/SRVHYLOrd9Z"
    "FQyXBM1myq+NYSkICxCsZLvKh7EO21XTYJ6dn5epD3Z+nl8gDO8l8IztmeW3xRRdk3EHja"
    "kMe2GWqsNkJ01O0jJxLE1Oh8DYZdXglGq1quqyr9psWHHZ1xnayeU8ZXarZZYDRPLVzlIq"
    "ZzVtM0MbjCmBjuho5yi+2SOjS+TaM/ndImOj8C4GDWhUEb0j/dHKC2ipcB1jCXg+Z1JbVQ"
    "gvlajnVkJeFT8QBgtg7EBUf0+PkDrpWhJXvk4KQqhGABq9kmYap6pHP906kluuFSxlWSnL"
    "SpFHyrKHxFjpPq3PFpIh+JTEL4PykECUHtRteVCjC6sGDBM+vO7imPHBtSkM/oo7Af3OYB"
    "lKbez+cZFmK9yJati0bKV6m491NXek1PTq1vQELys5fZYUndTwtuHukUqeVPKkLtCTSt4B"
    "Mbaqw2Kbok2f2kybZQk1/p1CcYaEY7Ypx0jRpWbR5Rn0looBKxGSboZPbUV8wU+jAoj+8G"
    "4CuJX4M/hFN7Py2j8e7m5zhJSQJHmQMc1V/k8J2h22D9AC/PB9Y6dVKp8vmbqXOIZwgvdZ"
    "1ptdHix//j8lD6aQ"
)
