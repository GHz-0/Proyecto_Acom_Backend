# Proyecto integrador: Sistema de gestión de ACOM (Actividades Complementarias — TecNM)

Proyecto para Desarrollo Web Avanzado: **lo construyen los alumnos** desde cero. Ejercita lo visto en las Unidades 1 y 3 (buenas prácticas, patrones de diseño, MVT, instalación y estructura de un framework) sobre un caso de uso reconocible para cualquier estudiante del TecNM.

Este documento es el enunciado: describe el problema, qué debe hacer el sistema y cómo se evalúa. No incluye código base.

## El problema real que resuelve

En el Tecnológico Nacional de México, las **ACOM (Actividades Complementarias)** son un requisito obligatorio para titularse: cada estudiante debe acumular **5 créditos complementarios** a lo largo de la carrera, en actividades que **no son materias del plan de estudios** — investigación, cursos/diplomados, publicaciones, cultura/deporte, tutorías, o impacto social.

El proceso de acreditación tiene tres pasos con tres responsables distintos:

```
Estudiante                Responsable de la              Departamento
                          actividad (docente/                Académico
                          entrenador/tutor)
    │                            │                              │
    │  1. Se inscribe             │                              │
    ├────────────────────────────►│                              │
    │                            │  2. Evalúa desempeño          │
    │                            │     y emite constancia        │
    │                            ├─────────────────────────────►│
    │                            │                              │  3. Valida constancia
    │                            │                              │     y registra créditos
    │◄──────────────────────────────────────────────────────────┤     en el expediente
    │        Créditos visibles en su expediente (SITEC/SII)       │
```

El sistema debe modelar ese flujo: **inscripción → evaluación → constancia → validación y registro de créditos**, con un límite de 5 créditos y reglas de quién puede hacer qué en cada paso.

## Categorías de actividad (según el modelo oficial del TecNM)

| Categoría | Ejemplos |
|---|---|
| Investigación y desarrollo tecnológico | Veranos de investigación, proyectos con docentes, InnovatecNM, prototipos, patentes |
| Cursos, talleres y diplomados | Software especializado, lenguajes de programación, certificaciones |
| Publicaciones y ponencias | Artículos científicos, memorias de congreso, ponente |
| Actividades culturales y deportivas | Selecciones del instituto, música, danza, teatro |
| Tutorías y asesorías | Tutor entre pares, apoyo académico institucional |
| Impacto social y ambiente | Protección ambiental, brigadas, actividades comunitarias |

## Requisitos funcionales

1. **Actividades:** el Departamento Académico da de alta actividades con nombre, categoría, descripción, responsable, valor en créditos y estado activa/inactiva.
2. **Inscripción:** el estudiante ve las actividades activas y se inscribe. No puede inscribirse dos veces a la misma actividad.
3. **Evaluación:** el responsable de la actividad la evalúa (aprobado o rechazado, con observaciones). Solo ese responsable puede hacerlo.
4. **Constancia:** para una inscripción aprobada se emite una constancia con folio único (por ejemplo, `ACOM-000001`).
5. **Validación:** el Departamento Académico valida la constancia y registra los créditos en el expediente del estudiante.
6. **Consulta:** el estudiante ve sus inscripciones, los créditos acumulados y cuántos le faltan.

## Modelo de datos mínimo

Punto de partida; los alumnos pueden ampliarlo y justificar los cambios.

```
ActividadComplementaria
├── nombre, categoria, descripcion
├── responsable (FK User)       ← quién evalúa esta actividad
├── creditos_valor (decimal)
└── activa (bool)

Inscripcion
├── estudiante (FK User), actividad (FK)
├── estado: inscrito → evaluado_aprobado/rechazado → constancia_emitida → validado
├── fecha_inscripcion, fecha_evaluacion, observaciones
└── constraint: un estudiante no puede inscribirse dos veces a la misma actividad

Constancia (1 a 1 con Inscripcion)
├── folio (único, autogenerado)
├── fecha_emision, emitida_por (FK User)

RegistroCreditos (1 a 1 con Inscripcion)
├── creditos_otorgados, fecha_registro, validado_por (FK User)
```

## Reglas de negocio

- Solo el **responsable de la actividad** puede evaluarla.
- No se puede emitir constancia sin haber evaluado y aprobado primero.
- No se puede validar ni registrar créditos sin constancia emitida.
- Si el estudiante **ya alcanzó los 5.00 créditos**, un nuevo registro se rechaza con un error propio.
- Cada transición de estado inválida debe fallar con una excepción propia, no con un `if` suelto en la vista.
- Al validar y registrar, el sistema avisa mediante una señal (Observer) a quien quiera reaccionar, por ejemplo para notificar al estudiante, sin que el servicio dependa de ello.

## Arquitectura por capas (requisito de diseño)

El proyecto debe organizarse en **cuatro capas** con una regla de dependencia: cada capa solo importa de las de abajo, y el dominio no importa nada de Django.

```
┌──────────────────────────────────────────────┐
│ 1. PRESENTACIÓN   views · forms · templates  │  HTTP, validación de entrada
├──────────────────────────────────────────────┤
│ 2. APLICACIÓN     services/ (casos de uso)   │  orquesta, transacciones, permisos
├──────────────────────────────────────────────┤
│ 3. DOMINIO        domain/ (reglas puras)     │  estados, límites, excepciones
├──────────────────────────────────────────────┤
│ 4. INFRAESTRUCTURA models · selectors · signals · receivers │  ORM, correo, SITEC
└──────────────────────────────────────────────┘
```

### Estructura de carpetas sugerida

```
acom/
├── domain/
│   ├── estados.py         # EstadoInscripcion + TRANSICIONES permitidas (dict)
│   ├── reglas.py          # puede_evaluar(), excede_limite(): funciones puras
│   └── exceptions.py      # AcomError (base), TransicionInvalidaError, LimiteCreditosError
├── models.py              # solo campos, constraints y __str__
├── selectors.py           # lecturas: inscripciones_de(), total_validado()
├── services/
│   ├── inscripciones.py   # inscribir, evaluar, emitir_constancia, validar_y_registrar
│   └── permisos.py        # quién puede ejecutar cada caso de uso
├── signals.py / receivers.py
├── views/                 # delgadas: parsean, llaman al servicio, renderizan
├── forms.py
└── tests/
    ├── test_domain.py     # sin base de datos
    ├── test_services.py
    └── test_views.py
```

### Responsabilidad de cada capa

| Capa | Responsabilidad |
|---|---|
| **Dominio** | Máquina de estados como dato y reglas puras, sin ORM |
| **Infraestructura** | Lecturas en `selectors.py`, escrituras por ORM, signals y receivers |
| **Aplicación** | Un caso de uso por función, con `atomic()`, `select_for_update` y comprobación de permisos |
| **Presentación** | Traducir HTTP a llamadas y las excepciones a mensajes para el usuario |

### Idea central: las reglas como dato, los casos de uso como orquesta

Ilustración de la idea, no código para copiar:

```python
# domain/estados.py — la regla es un dato, no ifs dispersos
TRANSICIONES = {
    EstadoInscripcion.INSCRITO: {EVALUADO_APROBADO, EVALUADO_RECHAZADO},
    EstadoInscripcion.EVALUADO_APROBADO: {CONSTANCIA_EMITIDA},
    EstadoInscripcion.CONSTANCIA_EMITIDA: {VALIDADO},
}

def validar_transicion(actual, nuevo):
    if nuevo not in TRANSICIONES.get(actual, set()):
        raise TransicionInvalidaError(f"{actual} → {nuevo} no permitido")
```

```python
# services/inscripciones.py — el caso de uso coordina las capas
@transaction.atomic
def validar_y_registrar(inscripcion_id, usuario):
    permisos.exigir(usuario, "acom.can_validate_credits")
    insc = Inscripcion.objects.select_for_update().get(pk=inscripcion_id)
    validar_transicion(insc.estado, EstadoInscripcion.VALIDADO)
    if reglas.excede_limite(selectors.total_validado(insc.estudiante)):
        raise LimiteCreditosError(...)
    ...
    transaction.on_commit(lambda: inscripcion_validada.send(...))
```

### Trampas que la arquitectura debe evitar

- **Autorización:** debe centralizarse en `permisos.py` y llamarse desde el servicio, no desde cada vista. Un estudiante no debe poder validar créditos.
- **Concurrencia:** dos validaciones simultáneas no deben sobrepasar el límite de créditos. Usa `select_for_update`, y dispara la señal con `transaction.on_commit`.
- **Manejo de errores:** una doble inscripción no debe devolver un 500. Las vistas capturan `AcomError`, clase base de las excepciones propias.

## Cómo montarlo

```bash
django-admin startproject config .
python manage.py startapp acom

# En config/settings.py:  INSTALLED_APPS += ["acom"]
# En config/urls.py:      path("acom/", include("acom.urls"))

python manage.py makemigrations acom
python manage.py migrate
python manage.py createsuperuser        # para entrar a /admin/ y crear actividades de prueba
python manage.py test acom
python manage.py runserver
```

Flujo manual para probarlo en el navegador:

1. Entra a `/admin/` y crea un usuario responsable, un usuario de departamento y una actividad.
2. Como estudiante, entra a `/acom/` e inscríbete.
3. Como responsable, evalúa y emite la constancia.
4. Como departamento, valida y registra los créditos.
5. Vuelve a `/acom/mis-inscripciones/` como estudiante y verifica el crédito reflejado.

## Extensiones opcionales

- Agrega un campo `limite_cupo` a la actividad y una excepción propia cuando se alcance.
- Agrega una vista de reporte para el Departamento Académico: estudiantes con sus créditos acumulados y los que les faltan.
- Convierte los paneles a Class-Based Views y compara la legibilidad contra las funciones.
- Agrega un permiso de Django (`acom.can_validate_credits`) y restringe el panel del departamento con él.
- Escribe un receptor de la señal que envíe un correo real (backend de consola en desarrollo).
- Agrega un modelo `Periodo` (semestre) y un historial de transiciones de estado.

## Evaluación sugerida

| Evidencia | Qué valora |
|---|---|
| Pruebas pasando (dominio, servicios y vistas) | La lógica de negocio y el flujo HTTP funcionan de extremo a extremo |
| Cobertura de casos límite: autorización, doble inscripción, rechazo, límite de créditos | Pruebas más allá del camino feliz |
| Diagrama de estados de `Inscripcion` dibujado por el estudiante | Comprensión del flujo de tres responsables |
| Respeto de la regla de dependencia entre capas | Arquitectura, no solo funcionalidad |
| Explicación oral de dónde vive cada patrón (MVT, Service Layer, Observer) | Conexión explícita con la Unidad 1 |
