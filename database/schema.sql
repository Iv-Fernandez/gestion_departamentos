PRAGMA foreign_keys = ON;

-- Tabla de Usuarios para el software (Login)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre_completo TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'conserje',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Departamentos adaptada a las fichas reales
CREATE TABLE IF NOT EXISTS departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bloque TEXT NOT NULL,                  -- Ej: 'BLOCK 2613'
    numero_depto TEXT NOT NULL,            -- Ej: 'A-11'
    fojas TEXT,                            -- FS
    numero_inscripcion TEXT,               -- NUMERO
    ano_inscripcion INTEGER,               -- AÑO
    rol_sii TEXT,                          -- ROL
    avaluo_fiscal REAL,                    -- AVALUO
    observaciones TEXT,                    -- OBCERBACIONES
    UNIQUE(bloque, numero_depto)
);

-- Tabla de Integrantes / Grupo Familiar
CREATE TABLE IF NOT EXISTS integrantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    departamento_id INTEGER NOT NULL,
    parentesco TEXT NOT NULL,              -- 'PROPIETARIO', 'CONYUGE', 'HIJO', 'ARRENDATARIO', etc.
    nombres TEXT,
    apellido_paterno TEXT,
    apellido_materno TEXT,
    rut TEXT,
    fecha_nacimiento DATE,
    asistencia_reuniones TEXT DEFAULT 'NO',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE CASCADE
);