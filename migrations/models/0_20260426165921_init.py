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
    "Ecixg/cyEWeTG8uP/weoHDWJ"
)
