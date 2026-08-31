#  Sistema de Gestión de Departamentos y Residentes

Aplicación de escritorio desarrollada en Python para la administración, consulta, registro y auditoría de copropietarios y residentes en bloques habitacionales y condominios. Permite centralizar la información legal de las propiedades (Rol SII, Avalúo Fiscal, Fojas e Inscripción CBR) y la gestión del grupo familiar asociado a cada departamento.

---

##  Características Principales

* **Autenticación y Seguridad:** Sistema de inicio de sesión con control de roles y almacenamiento seguro de contraseñas mediante hashing SHA-256.
* **Consulta General Interactiva:** Visualización consolidada por departamento (1 fila por propiedad con titular asociado) y motor de búsqueda en tiempo real por Block, N° Depto, RUT o Nombre.
* **Ordenamiento Dinámico:** Ordenamiento ascendente/descendente al hacer clic en los encabezados de las columnas de la tabla.
* **Ficha Detallada y Edición:** Ventana modal centralizada para inspeccionar y modificar datos legales de la propiedad y gestionar habitantes (agregar o eliminar residentes de forma individual).
* **Registro Manual con Validación Previa:** Formulario de alta manual con validación inmediata para prevenir el ingreso de departamentos duplicados.
* **Procesamiento de Archivos Excel:**
  * Importación masiva por carpetas de bloques o fichas individuales (`.xlsx`).
  * Normalización automática de la numeración de bloques durante la carga.
  * Exportación de la base de datos completa a un archivo consolidado en Excel.
* **Persistencia Local:** Almacenamiento desacoplado y portable mediante SQLite.
