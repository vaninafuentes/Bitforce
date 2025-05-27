# 🏋️ Bitforce - Sistema de Gestión de Turnos para Gimnasios

**Bitforce** es una aplicación web diseñada para simplificar y automatizar la gestión de turnos en gimnasios, centros deportivos y espacios de entrenamiento. La plataforma permite a los usuarios reservar horarios para actividades específicas, mientras que los administradores gestionan la disponibilidad, los cupos, las actividades y los instructores.

## 🚀 Funcionalidades Principales

### 👤 Para Usuarios del Gimnasio (GymUser)
- **Reservar turnos** según actividad, sucursal y horario.
- **Ver disponibilidad de turnos** en tiempo real.
- **Cancelar turnos reservados**.
- **Consultar historial de reservas y asistencia**.

### 🛠️ Para Administradores
- **Administrar usuarios**: altas, bajas y modificaciones.
- **Gestionar actividades**: crear, editar, asignar coaches y definir capacidad máxima.
- **Administrar turnos**: establecer horarios disponibles y gestionar la ocupación.
- **Manejo de sucursales**: cada sede puede tener sus propias actividades y entrenadores.

## 🧩 Arquitectura del Sistema

### 🗃️ Modelo de Base de Datos
Relaciones clave:
- Un usuario puede reservar múltiples turnos.
- Cada turno está vinculado a una **sucursal** y una **actividad**.
- Las actividades tienen un **coach** asignado.
- Cada sucursal ofrece varias actividades.

## 📌 Notas finales

Bitforce busca ofrecer una experiencia eficiente, intuitiva y adaptable para mejorar la gestión del gimnasio, automatizando procesos repetitivos y facilitando la interacción entre usuarios, coaches y administradores.


