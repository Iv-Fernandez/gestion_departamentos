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
    bloque TEXT NOT NULL,                  
    numero_depto TEXT NOT NULL,            
    fojas TEXT,                           
    numero_inscripcion TEXT,               
    ano_inscripcion INTEGER,               
    rol_sii TEXT,                          
    avaluo_fiscal REAL,                    
    observaciones TEXT,                    
    UNIQUE(bloque, numero_depto)
);

-- Tabla de Integrantes / Grupo Familiar
CREATE TABLE IF NOT EXISTS integrantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    departamento_id INTEGER NOT NULL,
    parentesco TEXT NOT NULL,              
    nombres TEXT,
    apellido_paterno TEXT,
    apellido_materno TEXT,
    rut TEXT,
    fecha_nacimiento DATE,
    asistencia_reuniones TEXT DEFAULT 'NO',
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE CASCADE
);