# ACOM por capas — proyecto de estudio

Sistema de Actividades Complementarias (TecNM) organizado en **cuatro capas**. Está hecho para **leerse, ejecutarse y explicarse**, no para construirse desde cero. El enunciado del problema está en [`../README.md`](../README.md).

## Puesta en marcha

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py test              # 30 pruebas (24 de acom + 6 de api)
uv run ruff check --no-fix acom api config
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Para probar el flujo en el navegador, entra a `/admin/`, crea un responsable, un usuario de departamento (dale el permiso *Puede validar constancias y registrar créditos*) y una actividad. Después usa `/acom/`.

## API REST (`api/`) — una segunda capa de presentación

La misma lógica de negocio (`acom.services`, `acom.selectors`) también se expone como API REST versionada — la prueba de que la capa de Aplicación no sabe ni le importa si quien la llama es un navegador con HTML o un cliente JSON. Nada en `services/` ni `domain/` cambió para que esto funcionara.

- **Base:** `/api/v1/` — un futuro cambio incompatible viviría en `/api/v2/`, sin tocar `v1`.
- **Documentación interactiva:** `/api/docs/` (Swagger UI) y `/api/redoc/` (Redoc) — generadas automáticamente por `drf-spectacular` a partir del código, nunca escritas a mano.
- **Autenticación:** JWT (`djangorestframework-simplejwt`) — `POST /api/v1/auth/token/` con `username`/`password` devuelve `access`/`refresh`.

```bash
# 1. Login — obtener el token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "tu_usuario", "password": "tu_password"}'

# 2. Usar el token en cada petición protegida
curl http://localhost:8000/api/v1/actividades/ \
     -H "Authorization: Bearer <access_token>"
```

| Endpoint | Método | Rol | Delegación |
|---|---|---|---|
| `/api/v1/actividades/` | GET | Cualquiera autenticado | `selectors.actividades_activas` |
| `/api/v1/actividades/<id>/inscribirse/` | POST | Estudiante | `services.inscripciones.inscribir` |
| `/api/v1/mis-inscripciones/` | GET | Estudiante | `selectors.inscripciones_de` |
| `/api/v1/mis-inscripciones/resumen/` | GET | Estudiante | `selectors.total_validado` + `domain.reglas.faltantes` |
| `/api/v1/responsable/inscripciones/<id>/` | GET | Responsable de la actividad | `selectors.inscripcion_de_responsable` |
| `/api/v1/responsable/inscripciones/<id>/evaluar/` | POST | Responsable | `services.inscripciones.evaluar` |
| `/api/v1/responsable/inscripciones/<id>/emitir-constancia/` | POST | Responsable | `services.inscripciones.emitir_constancia` |
| `/api/v1/departamento/inscripciones/<id>/validar/` | POST | Departamento (`can_validate_credits`) | `services.inscripciones.validar_y_registrar` |

Los errores de negocio (`AcomError` y subclases) se traducen a HTTP en un solo lugar: `api/exceptions.py` — el mismo principio de "una sola fuente de verdad" que ya usa `services/permisos.py` para las reglas de autorización.

## Las capas y la regla de dependencia

Cada capa solo importa de las de abajo. El dominio no importa nada de Django (lo verifica `ReglaDeDependenciaTest`).

```
┌──────────────────────────────────────────────┐
│ 1. PRESENTACIÓN   views/ · forms.py · templates/ │
├──────────────────────────────────────────────┤
│ 2. APLICACIÓN     services/                  │
├──────────────────────────────────────────────┤
│ 3. DOMINIO        domain/                    │
├──────────────────────────────────────────────┤
│ 4. INFRAESTRUCTURA models.py · selectors.py · signals.py · receivers.py │
└──────────────────────────────────────────────┘
```

| Capa | Archivos | Responsabilidad |
|---|---|---|
| Presentación | `views/`, `forms.py`, `templates/acom/` | Traduce HTTP a llamadas y `AcomError` a mensajes. No decide reglas. |
| Aplicación | `services/inscripciones.py`, `services/permisos.py` | Un caso de uso por función: permisos, transacción, bloqueos, orquestación. |
| Dominio | `domain/estados.py`, `reglas.py`, `exceptions.py` | Máquina de estados como dato y reglas puras. Sin ORM. |
| Infraestructura | `models.py`, `selectors.py`, `signals.py`, `receivers.py` | Acceso a datos, lecturas y reacciones a eventos. |

## Dinámica por equipos

Un equipo por capa. Cada equipo prepara una explicación de **10 minutos** con evidencia:

1. Qué hace su capa y por qué cada archivo vive ahí y no en otra.
2. Una demostración ejecutando código o una prueba real.
3. Qué se rompería si su capa importara de la de arriba.
4. Cómo se conecta con la capa vecina (entrada y salida).

### Preguntas guía por capa

**Dominio**
- ¿Por qué `TRANSICIONES` es un diccionario y no una cadena de `if`?
- Ejecuta solo `test_domain.py`. ¿Por qué corre sin base de datos?
- ¿Por qué `EstadoInscripcion` es un `StrEnum` y no un `TextChoices` de Django?

**Infraestructura**
- ¿Por qué `models.py` no tiene reglas de negocio? ¿Qué pasa con `CheckConstraint` y `UniqueConstraint`: ¿son reglas o son datos?
- ¿Qué gana `selectors.py` frente a consultas directas en las vistas?
- Observa `total_validado`: ¿por qué hace `quantize`? (Pista: pruébalo sin esa línea.)

**Aplicación**
- Mira `validar_y_registrar`: ¿por qué bloquea al **estudiante** además de la inscripción? ¿Qué carrera evita?
- ¿Por qué la señal se envía con `transaction.on_commit`? Explica qué pasaría sin él.
- ¿Por qué la autorización está aquí y no en las vistas? Compara con `panel_departamento`, que además usa un decorador.

**Presentación**
- ¿Por qué las vistas capturan `AcomError` y no cada excepción por separado?
- ¿Qué respuesta HTTP recibe un estudiante que intenta validar créditos? ¿Y un docente ajeno al abrir un panel? ¿Por qué distintas?
- ¿Qué hace `test_doble_inscripcion_muestra_error_y_no_500`?

> **Plan de 2 semanas para 7 equipos:** funcionalidades del lineamiento TecNM en [`PLAN_EQUIPOS.md`](PLAN_EQUIPOS.md).

## Ronda final: la extensión que atraviesa todas las capas

En equipos mezclados (una persona de cada capa), agreguen **`limite_cupo`** a la actividad. Deben tocar las cuatro capas y no pueden saltarse ninguna:

1. **Infraestructura:** campo nuevo y migración.
2. **Dominio:** `CupoLlenoError` (hereda de `AcomError`) y una regla pura `cupo_disponible(...)`.
3. **Aplicación:** `inscribir` valida el cupo.
4. **Presentación:** el formulario de inscripción muestra el error.
5. **Pruebas** en cada capa; la de dominio sin base de datos.

## Evaluación

| Evidencia | Qué valora |
|---|---|
| Explicación con demostración | Entender la capa, no repetir definiciones |
| Respuesta a "qué se rompería si..." | Comprender la regla de dependencia |
| Extensión `limite_cupo` con pruebas en cada capa | Aplicar el patrón, no solo describirlo |
| Coevaluación entre equipos | Participación en la discusión de fronteras |
