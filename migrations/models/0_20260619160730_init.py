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
    "qr_generated_at" TIMESTAMP,
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
    "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"
    "D5Y//x9q76D0"
)
