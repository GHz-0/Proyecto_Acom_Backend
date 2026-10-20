# Plan de trabajo — 7 equipos extienden ACOM según el lineamiento TecNM

**Duración:** 2 semanas (10 días hábiles). **Base:** el código actual de `acom_backend` (4 capas + API v1 con JWT).
**Fuente de requisitos:** *Lineamiento para la Acreditación de Actividades Complementarias* del TecNM (documento compartido en clase).

Cada equipo implementa **una funcionalidad** que falta respecto al lineamiento. Todas atraviesan las cuatro capas (Infraestructura → Dominio → Aplicación → Presentación) y la API. La regla de dependencia del [`README.md`](README.md) sigue vigente: nadie puede saltarse una capa.

> `limite_cupo` **no** es parte de este plan: sigue siendo la *Ronda final* del README.

---

## Resumen para el estudiante: qué es esto, en términos de usuario final

Antes de los comandos y las tablas técnicas, esto es lo que estás construyendo, explicado como si fueras la persona que **usa** el sistema, no quien lo programa.

### ¿Qué es ACOM?

Es el sistema donde un estudiante del TecNM registra sus "actividades complementarias" (un curso, una certificación, un torneo deportivo, una brigada social, etc.) para que le cuenten como créditos obligatorios de su carrera — hoy en día, en la vida real, esto se hace a mano con papeles y firmas. Ustedes están construyendo la versión digital.

### Los 3 tipos de persona que van a usar lo que programen

| Rol | Qué hace en el sistema (sin tecnicismos) |
|---|---|
| **Estudiante** | Entra, ve el catálogo de actividades disponibles, se inscribe a una, y cuando la termina puede ver/descargar su constancia y revisar cuántos créditos le faltan. |
| **Responsable de área** (quien organiza la actividad) | Revisa quién se inscribió, registra si cumplió (horas, asistencia), y aprueba o rechaza. Al aprobar, se genera la constancia. |
| **Departamento** (quien administra todo el programa) | Ve el avance de todos los estudiantes, detecta quién ya cumplió sus 5 créditos y puede "liberarlo" (darle de alta como completado) para que siga su trámite de titulación. |

### Lo que cada uno de los 7 equipos debe hacer, explicado sin jerga técnica

**E1 — Catálogo oficial de campos y tipos de actividad**
- Reemplazar las categorías actuales (inventadas) por los 6 campos oficiales del lineamiento.
- Armar la lista de tipos de actividad que entran en cada campo (ej. "idiomas" entra en Actividades formativas), con datos reales, no de ejemplo.
- Lograr que cada actividad del catálogo diga a qué campo y tipo pertenece, y que no se pueda mezclar un tipo con el campo equivocado.
- Resultado que el usuario ve: el catálogo de actividades está ordenado por los 6 campos oficiales, no por categorías sueltas.

**E2 — Horas y valor en créditos**
- Definir la regla oficial: 20 horas = 1 crédito.
- Hacer que cada actividad calcule sola sus créditos a partir de las horas que pide, y bloquear cualquier actividad que termine valiendo menos de 1 o más de 2 créditos.
- Mostrar esas horas y créditos en pantalla y en la API.
- Resultado que el usuario ve: cada actividad dice cuántas horas necesita y cuántos créditos vale, con el cálculo correcto.

**E3 — Límite de créditos por campo**
- Definir cuántos créditos como máximo se pueden acumular en un solo campo (según el lineamiento).
- Hacer que el sistema cuente los créditos ya validados por campo para cada estudiante.
- Bloquear con un mensaje claro cualquier intento de validar un crédito que exceda ese límite en un campo.
- Resultado que el usuario ve: no se puede "hacer trampa" acumulando todos los créditos en un solo tipo de actividad.

**E4 — Registro de horas cumplidas**
- Crear la forma de registrar, actividad por actividad, cuántas horas de verdad cumplió cada estudiante (no basta con que se haya inscrito).
- Hacer que solo el responsable de la actividad pueda registrar esas horas.
- Bloquear la aprobación de una actividad si no se cumplieron las horas mínimas requeridas.
- Resultado que el usuario ve: inscribirse ya no es suficiente — hay que demostrar que se cumplieron las horas antes de que cuente.

**E5 — Periodos escolares y fechas de inscripción**
- Crear el concepto de "periodo escolar" (ej. 2026-2) con fecha de inicio y fin.
- Hacer que cada actividad tenga una ventana de fechas en la que se puede inscribir gente.
- Bloquear, con un mensaje claro, cualquier inscripción fuera de esa ventana.
- Resultado que el usuario ve: las actividades solo se pueden ofertar e inscribir dentro de fechas concretas, no todo el año sin control.

**E6 — Constancia de acreditación descargable**
- Diseñar el formato de la constancia oficial (los datos que exige el lineamiento: folio, estudiante, actividad, campo, horas, créditos, responsable, firma).
- Hacer que el sistema genere esa constancia automáticamente al aprobar una actividad.
- Permitir que el estudiante dueño y el responsable la vean/impriman, y bloquear a cualquier otra persona.
- Resultado que el usuario ve: hay una constancia real para imprimir, no solo un mensaje de "aprobado" en pantalla.

**E7 — Kárdex y avance por campo**
- Calcular, para cada estudiante, cuántos créditos lleva en total y desglosados por cada uno de los 6 campos.
- Definir cuándo un estudiante ya cumplió todo lo necesario (5 créditos, sin pasarse del límite por campo) y puede "liberarse".
- Mostrar ese resumen al estudiante y una lista de estudiantes liberables al departamento.
- Resultado que el usuario ve: el estudiante (y el departamento) ve de un vistazo cuánto le falta y si ya puede titularse.

### Por qué importa trabajar en equipo bien (no solo "para la calificación")

Si tu equipo rompe algo que otro equipo ya tenía funcionando (una prueba, un endpoint), **el usuario final sufre eso en la vida real** — así de literal es la metáfora: en un sistema real, un estudiante no podría ver su constancia porque el equipo de kárdex rompió algo sin darse cuenta. Por eso el plan insiste tanto en pruebas en verde y revisión cruzada antes de cada merge.

---

## 0. Antes de empezar: cómo se trabaja en equipo con Git, paso a paso

Si nunca has colaborado en un repositorio compartido con otras personas, lee esto completo antes del Día 1 — asume cero experiencia previa. Si necesitas repasar conceptos base de Git (qué es un commit, una rama, cómo resolver un conflicto), ya los viste en [`../../../curso_git/README.md`](../../../curso_git/README.md) y [`../../../git_avanzado/README.md`](../../../git_avanzado/README.md) — aquí solo se explica **cómo se aplica eso específicamente a este proyecto**.

### Glosario mínimo (si algo no te suena, es normal)

| Término | En una frase |
|---|---|
| **Rama (branch)** | Una copia paralela del código donde puedes experimentar sin afectar el trabajo de los demás equipos. |
| **Commit** | Una "foto" guardada de tus cambios, con un mensaje que explica qué hiciste. |
| **Push** | Subir tus commits locales al repositorio compartido (GitHub). |
| **Pull** | Bajar a tu máquina los cambios que otros ya subieron. |
| **Pull Request (PR)** | Una solicitud formal de "aquí está mi rama terminada, revísenla antes de mezclarla con `main`". |
| **Merge** | El acto de mezclar una rama (ya revisada) dentro de `main`. |
| **Conflicto** | Cuando dos personas editaron la misma línea del mismo archivo y Git no puede decidir solo cuál versión usar. |
| **`main`** | La rama "oficial" del proyecto — lo que está en `main` es lo que funciona de verdad, para todos. |

### Paso a paso — lo que hace tu equipo el Día 1, literalmente comando por comando

**1. Clonar el repositorio (solo una persona del equipo, o cada quien si prefieren trabajar por separado):**
```bash
git clone <url-del-repositorio>
cd curso-python/desarrollo_web_avanzado/proyecto_acom/acom_backend
```

**2. Crear la rama de tu equipo, a partir de `main` actualizado:**
```bash
git checkout main
git pull origin main          # asegúrate de partir de la versión más reciente
git checkout -b equipo-1/catalogo-campos   # el nombre exacto de tu equipo, de la sección 4
```

**3. Trabajar normal — editar archivos, correr pruebas, repetir:**
```bash
uv run python manage.py test
uv run ruff check --no-fix acom api config
```

**4. Guardar tu avance en commits pequeños y frecuentes (no un solo commit gigante al final):**
```bash
git add acom/domain/reglas.py acom/domain/exceptions.py
git commit -m "Agrega regla tipo_pertenece_a_campo y error TipoNoCorrespondeError"

# ...sigues trabajando...

git add acom/models.py acom/migrations/
git commit -m "Agrega modelo TipoActividad y migración de datos del catálogo"
```

> Un commit por **cada pieza que funciona por sí sola** (un modelo, una regla, un endpoint) — no esperes a terminar todo para hacer el primer commit. Si algo sale mal, puedes regresar al último commit bueno sin perder todo el trabajo.

**5. Subir tu rama a GitHub (la primera vez necesita `-u`, después basta `git push`):**
```bash
git push -u origin equipo-1/catalogo-campos
```

**6. Abrir el Pull Request cuando tu funcionalidad esté lista (con pruebas en verde):**
```bash
gh pr create --title "E1: Catálogo oficial de campos y tipos de actividad" --body "Implementa el catálogo de 6 campos del lineamiento. Pruebas: uv run python manage.py test (verde). Swagger: GET /api/v1/campos/"
```
Si no tienen `gh` instalado, se hace igual desde la página de GitHub: entra al repositorio, pestaña **Pull requests → New pull request**, elige tu rama, y llena título y descripción.

**7. Pedir la revisión al equipo que les toca según la rotación (sección 4) y esperar su aprobación antes de mezclar.**

**8. Una vez aprobado y mezclado a `main`, todos los equipos actualizan su copia local antes de seguir trabajando:**
```bash
git checkout main
git pull origin main
git checkout equipo-2/horas-creditos   # tu propia rama
git merge main                          # trae los cambios nuevos de main a tu rama
```

### Cómo dividirse el trabajo **dentro** de un equipo de 3-5 personas

La funcionalidad de tu equipo atraviesa las cuatro capas, pero **no tienen que hacerlas en fila, una persona esperando a que la otra termine**. Repártanse así desde el primer día:

1. **Una persona** diseña y escribe las funciones de **Dominio** primero (son las más simples: reciben valores, devuelven valores, sin base de datos) — esto desbloquea a los demás porque ya pueden importar esas funciones aunque el resto no esté listo.
2. **Otra persona** en paralelo prepara **Infraestructura**: el modelo/campo nuevo y su migración, sin esperar a que el dominio esté terminado.
3. Cuando el dominio y la infraestructura ya existen (aunque sea una primera versión), **una tercera persona** conecta todo en **Aplicación** (el servicio).
4. **Presentación** (HTML + API) se hace al final, cuando el servicio ya funciona — y puede dividirse entre dos personas: una el HTML, otra los endpoints/serializers de la API.
5. **Las pruebas no son de una sola persona al final** — cada quien escribe la prueba de lo que acaba de programar, en el mismo commit o el siguiente.

**Si su equipo es de 3 personas:** una toma Dominio+Infraestructura, otra Aplicación, otra Presentación+API — y todos revisan el PR final juntos antes de pedir la revisión cruzada.

### Qué hacer si algo sale mal (antes de entrar en pánico)

| Problema | Qué hacer |
|---|---|
| "Hice `git push` y me rechazó, dice que hay cambios nuevos" | `git pull origin <tu-rama>` primero, resuelve lo que pida, y vuelve a intentar el push. |
| "Tengo un conflicto al hacer `git merge main`" | Repasa [`07_resolucion_conflictos.md`](../../../curso_git/07_resolucion_conflictos.md) — Git marca con `<<<<<<<` las líneas en conflicto; edita el archivo dejando la versión correcta, luego `git add` + `git commit`. |
| "Corrí las pruebas y ahora fallan cosas que yo no toqué" | Probablemente mezclaste `main` y algo de otro equipo rompió un *fixture* compartido — avisa en el canal del grupo, no lo arregles solo sin avisar. |
| "No sé si debo hacer commit de algo" | Si tu código corre y las pruebas relacionadas pasan, sí. Nunca subas un commit con pruebas en rojo a propósito "para después". |
| "Dos equipos tocaron el mismo archivo y hay conflicto de migraciones" | Ver sección 4, "Migraciones (riesgo principal)" — se borra y regenera la migración propia, nunca se edita la de otro equipo. |

---

## 1. Qué pide el lineamiento y qué falta en el código

| Lineamiento TecNM | Estado actual | Equipo |
|---|---|---|
| 6 campos de formación con nombres oficiales y un catálogo de actividades por campo | `CategoriaActividad` (`acom/models.py`) tiene 6 opciones con nombres distintos (p. ej. "Publicaciones y ponencias" ≠ "Actividades académicas y de vinculación"); no hay subtipos | **E1** |
| 20 horas ≈ 1 crédito; cada actividad vale entre 1 y 2 créditos | `creditos_valor` es libre (solo `> 0`) y no hay horas | **E2** |
| Una sola actividad o campo no puede dar todos los créditos (formación variada) | Solo existe el límite global `META_CREDITOS = 5` (`acom/domain/reglas.py`) | **E3** |
| Cumplir el mínimo de horas antes de acreditar | `evaluar` no revisa horas | **E4** |
| Las actividades se ofertan por periodo escolar | No hay periodo ni fechas de inscripción | **E5** |
| Constancia de acreditación firmada por el responsable del área | `Constancia` solo guarda el folio; no hay documento | **E6** |
| 5 créditos totales durante la carrera, repartidos entre campos | `resumen` solo da el total y lo que falta | **E7** |

---

## 2. Reglas comunes para todos los equipos

1. **Capas:** el dominio no importa Django (`ReglaDeDependenciaTest` en `acom/tests/test_domain.py` debe seguir pasando). Las reglas nuevas son funciones puras en `acom/domain/`.
2. **Errores:** cada error nuevo hereda de `AcomError` (`acom/domain/exceptions.py`). La API lo convierte en `400` sin cambios gracias a `api/exceptions.py`; si necesitan otro código, lo agregan **ahí** y en ningún otro lugar.
3. **Permisos:** solo en `acom/services/permisos.py` (reutilicen `exigir_responsable` y `exigir_permiso`).
4. **Lecturas:** toda consulta nueva es una función en `acom/selectors.py`; las vistas y los servicios no arman consultas.
5. **API v1:** solo cambios **aditivos**. No se borra ni renombra ningún campo ni endpoint existente. Documenten cada endpoint nuevo con `extend_schema` para que aparezca en `/api/docs/`.
6. **Pruebas mínimas por equipo:**
   - dominio con `SimpleTestCase` (sin base de datos);
   - servicio con `AcomTestCase` (`acom/tests/base.py`);
   - API con JWT, siguiendo el patrón de `autenticar_con_jwt` en `api/tests.py`.
7. **Calidad:** `uv run python manage.py test` y `uv run ruff check --no-fix acom api config` en verde antes de abrir el PR.

### Archivos compartidos (zona de conflictos)

`acom/models.py`, `acom/domain/exceptions.py`, `acom/domain/reglas.py`, `acom/services/inscripciones.py`, `acom/selectors.py`, `acom/tests/base.py`, `api/serializers.py`, `api/urls.py`, `api/exceptions.py`.

- **Solo agregar**, al final de su bloque. No reordenar, no reformatear código ajeno.
- Prefieran **archivos nuevos** para su código: `acom/services/horas.py`, `acom/services/periodos.py`, `api/views_kardex.py`, `acom/tests/test_horas.py`, etc.
- Si su funcionalidad obliga a cambiar los *fixtures* de `acom/tests/base.py` (E2, E3 y E4 casi seguro), avisen en el canal del grupo y hagan el cambio en un commit aparte y pequeño.

---

## 3. Fichas por equipo

### E1 — Catálogo oficial de campos y tipos de actividad · *Oleada 1*

**Lineamiento:** las actividades se agrupan en 6 campos de formación, y cada campo tiene un catálogo de actividades permitidas.

| Capa | Cambios |
|---|---|
| Infraestructura | Cambiar las **etiquetas** de `CategoriaActividad` a los 6 nombres oficiales (Tutoría; Actividades formativas / Cursos; Investigación y desarrollo tecnológico; Actividades académicas y de vinculación; Actividades culturales y deportivas; Compromiso social y ambiental). **No cambien los `value`** para no romper datos. Nuevo modelo `TipoActividad(campo, nombre, descripcion)` y FK opcional `ActividadComplementaria.tipo`. Migración de datos que cargue el catálogo del lineamiento (tutoría entre pares, certificación profesional, idiomas, InnovatecNM, verano de investigación, congreso, concurso académico, selección deportiva, brigada comunitaria, etc.). Registrar en `admin.py`. |
| Dominio | Regla pura `tipo_pertenece_a_campo(campo_tipo, campo_actividad) -> bool`. Error `TipoNoCorrespondeError`. |
| Aplicación | Servicio `asignar_tipo(actividad, tipo, usuario)` que valida la regla (solo el departamento, con `exigir_permiso`). |
| Presentación | HTML: mostrar campo y tipo en `lista_actividades.html`. API: `GET /api/v1/campos/` (campos con sus tipos) y `tipo` en `ActividadComplementariaSerializer`. |

**📅 Actividades diarias (días 1-5):**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Leer el lineamiento y anotar los 6 campos oficiales con 2-3 tipos de actividad por campo | Lista escrita de 6 campos + tipos (puede ser en la ficha de diseño) |
| 2 | Escribir `tipo_pertenece_a_campo()` y `TipoNoCorrespondeError`, con su prueba sin base de datos | `test_domain.py` nuevo, en verde |
| 3 | Crear el modelo `TipoActividad`, la FK en `ActividadComplementaria`, y la migración de datos con el catálogo completo | `uv run python manage.py migrate` corre sin error; `/admin/` muestra los tipos cargados |
| 4 | Servicio `asignar_tipo()` + endpoint `GET /api/v1/campos/` + campo `tipo` en el serializer | Endpoint visible y funcionando en `/api/docs/` |
| 5 (mañana) | Revisar pruebas y `ruff` en verde, abrir el PR | PR abierto con descripción clara |

**🎯 Meta del equipo:**
- [ ] Los 6 campos oficiales existen con los nombres exactos del lineamiento
- [ ] Cada campo tiene su catálogo de tipos cargado automáticamente por la migración de datos
- [ ] Asignar un tipo de un campo a una actividad de otro campo da un error claro (`TipoNoCorrespondeError`), no una excepción genérica de Django
- [ ] `GET /api/v1/campos/` aparece en Swagger y responde correctamente

**Aceptación (lo que se revisa al cerrar):** Swagger lista los 6 campos oficiales con sus tipos; una actividad no acepta un tipo de otro campo.

---

### E2 — Horas y valor en créditos · *Oleada 1*

**Lineamiento:** 20 horas equivalen a 1 crédito; cada actividad vale entre 1 y 2 créditos.

| Capa | Cambios |
|---|---|
| Infraestructura | Campo `horas_requeridas` (`PositiveIntegerField`) en `ActividadComplementaria`. `CheckConstraint` 1 ≤ `creditos_valor` ≤ 2. |
| Dominio | Constantes `HORAS_POR_CREDITO = 20`, `CREDITOS_MIN = 1`, `CREDITOS_MAX = 2`. Reglas puras `creditos_por_horas(horas) -> Decimal` y `creditos_en_rango(creditos) -> bool`. Error `CreditosFueraDeRangoError`. |
| Aplicación | Servicio `crear_actividad(...)` (o validación en un servicio existente) que calcule los créditos a partir de las horas y rechace valores fuera de rango. |
| Presentación | Mostrar horas y créditos en HTML. API: `horas_requeridas` en `ActividadComplementariaSerializer`. |

**Ojo:** `test_no_se_registran_creditos_pasado_el_limite` (`acom/tests/test_services.py`) crea una actividad de `3.00` créditos, que queda fuera de rango. Ajusten esa prueba para que siga probando el límite de 5 créditos con actividades de 1–2 créditos.

**📅 Actividades diarias (días 1-5):**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño: decidir dónde vive el cálculo horas→créditos (dominio) y confirmar las constantes del lineamiento | Ficha de diseño con `HORAS_POR_CREDITO`, `CREDITOS_MIN`/`MAX` |
| 2 | `creditos_por_horas()`, `creditos_en_rango()`, `CreditosFueraDeRangoError` + pruebas sin BD | `test_domain.py` en verde |
| 3 | Campo `horas_requeridas`, `CheckConstraint` 1-2 créditos, migración | `migrate` corre sin error |
| 4 | Servicio que calcule créditos desde horas y rechace fuera de rango; ajustar `test_no_se_registran_creditos_pasado_el_limite` | Pruebas de servicio en verde |
| 5 (mañana) | HTML + `horas_requeridas` en el serializer; PR | PR abierto |

**🎯 Meta del equipo:**
- [ ] 40 horas calculan automáticamente 2 créditos
- [ ] Una actividad de 3 créditos (o 0) no se puede guardar
- [ ] El test de límite global de 5 créditos sigue pasando con actividades de 1-2 créditos

**Aceptación (lo que se revisa al cerrar):** 40 horas dan 2 créditos; una actividad de 3 créditos no se puede guardar.

---

### E3 — Límite de créditos por campo · *Oleada 2 (depende de E1)*

**Lineamiento:** un solo campo no puede aportar todos los créditos, para garantizar una formación variada.

| Capa | Cambios |
|---|---|
| Infraestructura | Selector `total_validado_por_campo(estudiante, campo) -> Decimal`, con el mismo `quantize` que `total_validado`. |
| Dominio | Constante `MAX_CREDITOS_POR_CAMPO = Decimal("2.00")`. Regla pura `excede_limite_campo(total_campo, creditos_nuevos) -> bool`. Error `LimiteCampoError`. |
| Aplicación | `validar_y_registrar` revisa el límite por campo **después** de bloquear al estudiante (el `select_for_update` que ya existe también protege esta regla). |
| Presentación | El panel del departamento muestra el error; la API responde `400` con el mensaje. |

**Ojo:** los *fixtures* crean todas las actividades en `INVESTIGACION`. Agreguen un parámetro `categoria` a `crear_actividad` en `acom/tests/base.py` (con el valor actual como *default*) para que las pruebas de límite global sigan pasando.

**📅 Actividades diarias:**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño (en paralelo, aunque la implementación espere a E1): leer cómo queda `CategoriaActividad`, fijar `MAX_CREDITOS_POR_CAMPO` | Ficha de diseño |
| 2-5 | Mientras E1 no está mezclado: escribir `excede_limite_campo()` y `LimiteCampoError` + sus pruebas de dominio (no dependen de E1, son función pura) | `test_domain.py` en verde, sin tocar BD |
| 6 | `git pull origin main` (ya con E1 integrado); selector `total_validado_por_campo()` | Selector probado contra datos reales |
| 7 | `validar_y_registrar` revisa el límite por campo después de bloquear al estudiante | Prueba de servicio en verde |
| 8 | Parámetro `categoria` en `crear_actividad` (`acom/tests/base.py`); panel del departamento + API muestran el error | Pruebas existentes de límite global siguen pasando |
| 9 | Pruebas finales, revisión cruzada, PR | PR abierto |

**🎯 Meta del equipo:**
- [ ] Un estudiante con 2 créditos en un campo no puede validar otro crédito en ese mismo campo
- [ ] Sí puede validar créditos en un campo distinto
- [ ] El error se ve tanto en el panel del departamento como en la API (`400`)

**Aceptación (lo que se revisa al cerrar):** un estudiante con 2 créditos en Investigación no puede validar otro crédito en Investigación, pero sí en Tutoría.

---

### E4 — Registro de horas cumplidas · *Oleada 2 (depende de E2)*

**Lineamiento:** cada actividad exige un mínimo de horas cumplidas antes de acreditarse.

| Capa | Cambios |
|---|---|
| Infraestructura | Modelo `RegistroHoras(inscripcion, fecha, horas, registrado_por)` con `CheckConstraint` `horas > 0`. Selector `horas_acumuladas(inscripcion) -> int`. |
| Dominio | Regla pura `horas_cumplidas(acumuladas, requeridas) -> bool`. Error `HorasInsuficientesError`. |
| Aplicación | Nuevo `acom/services/horas.py` con `registrar_horas(inscripcion_id, usuario, fecha, horas)`: solo el responsable (`exigir_responsable`) y solo si la inscripción está en estado `INSCRITO`. `evaluar(aprobado=True)` exige horas cumplidas; rechazar no las exige. |
| Presentación | Formulario de horas en `panel_responsable.html`. API: `POST /api/v1/responsable/inscripciones/<id>/horas/` y horas acumuladas en el detalle. |

**Ojo:** `inscripcion_con_constancia` en `acom/tests/base.py` aprueba sin horas. Hagan que registre las horas requeridas antes de evaluar.

**📅 Actividades diarias:**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño: quién registra las horas (el responsable), qué datos guarda `RegistroHoras` | Ficha de diseño |
| 2-5 | Dominio: `horas_cumplidas()`, `HorasInsuficientesError` + pruebas (no depende de E2 para el dominio puro) | `test_domain.py` en verde |
| 6 | `git pull origin main` (ya con E2 integrado); modelo `RegistroHoras` + migración + selector `horas_acumuladas()` | `migrate` corre sin error |
| 7 | `acom/services/horas.py`: `registrar_horas()` (solo responsable, solo estado `INSCRITO`); `evaluar(aprobado=True)` exige horas | Prueba de servicio en verde |
| 8 | Ajustar `inscripcion_con_constancia` en `acom/tests/base.py`; formulario en `panel_responsable.html` + endpoint API | Pruebas existentes siguen pasando |
| 9 | Pruebas finales, PR | PR abierto |

**🎯 Meta del equipo:**
- [ ] No se puede aprobar una inscripción con menos horas de las requeridas (ej. 15 de 20)
- [ ] Con las horas completas (20 de 20), sí se puede aprobar
- [ ] El fixture compartido (`inscripcion_con_constancia`) sigue funcionando para los demás equipos

**Aceptación (lo que se revisa al cerrar):** no se puede aprobar una inscripción con 15 de 20 horas; con 20 sí.

---

### E5 — Periodos escolares y fechas de inscripción · *Oleada 2 (independiente)*

**Lineamiento:** las actividades se ofertan y acreditan dentro de un periodo escolar.

| Capa | Cambios |
|---|---|
| Infraestructura | Modelo `Periodo(clave, inicio, fin)` (p. ej. `"2026-2"`, clave única). FK opcional `periodo` y campos `inscripcion_abre` / `inscripcion_cierra` en `ActividadComplementaria`. `actividades_activas()` acepta un `periodo` opcional. |
| Dominio | Regla pura `inscripcion_abierta(hoy, abre, cierra) -> bool` (si no hay fechas, está abierta). Error `InscripcionCerradaError`. |
| Aplicación | `inscribir` valida la ventana de fechas (reciban `hoy` como parámetro o usen `timezone.localdate()` en el servicio, **nunca** en el dominio). |
| Presentación | HTML: mostrar la ventana de inscripción. API: filtro `GET /api/v1/actividades/?periodo=2026-2` y los campos nuevos en el serializer. |

**📅 Actividades diarias (días 1-8, equipo independiente):**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño: qué campos necesita `Periodo`, qué pasa con actividades sin periodo (retrocompatibilidad) | Ficha de diseño |
| 2-3 | Dominio: `inscripcion_abierta(hoy, abre, cierra)`, `InscripcionCerradaError` + pruebas con fechas fijas | `test_domain.py` en verde, sin `timezone.now()` |
| 4 | Infraestructura: modelo `Periodo`, FK y campos de fecha en `ActividadComplementaria`, migración (con *defaults* que no rompan datos existentes) | `migrate` corre sin error |
| 5-6 | Aplicación: `inscribir` valida la ventana (recibe `hoy` como parámetro; el dominio nunca llama al reloj real) | Prueba de servicio en verde |
| 7 | Presentación/API: filtro `?periodo=`, campos nuevos en el serializer, HTML | Endpoint probado en Swagger |
| 8 | `git pull origin main` (ya con E1/E2 integrados), resolver conflictos si los hay, pruebas finales, PR | PR abierto |

**🎯 Meta del equipo:**
- [ ] Existe el modelo `Periodo` con clave única
- [ ] Inscribirse fuera de la ventana de fechas da `400` con mensaje claro
- [ ] Las pruebas de dominio usan fechas fijas, nunca `datetime.now()` o `timezone.localdate()` dentro del dominio

**Aceptación (lo que se revisa al cerrar):** inscribirse fuera de la ventana devuelve `400` con mensaje claro; las pruebas de dominio usan fechas fijas, sin reloj real.

---

### E6 — Constancia de acreditación descargable · *Oleada 2 (independiente)*

**Lineamiento:** cada actividad requiere la Constancia de Acreditación firmada por el responsable del área.

| Capa | Cambios |
|---|---|
| Infraestructura | Campos `area_responsable` y `horas_acreditadas` en `Constancia` (valores por defecto para no romper registros existentes). Selector `constancia_de(inscripcion_id)`. |
| Dominio | Regla pura `puede_ver_constancia(usuario_id, estudiante_id, responsable_id) -> bool`. Reutilicen `generar_folio`. |
| Aplicación | `emitir_constancia` llena los campos nuevos. Servicio `obtener_constancia(inscripcion_id, usuario)` que autoriza con la regla anterior (en `permisos.py`). |
| Presentación | Plantilla imprimible `acom/templates/acom/constancia.html` (folio, estudiante, actividad, campo, horas, créditos, fecha, responsable y espacio de firma) y su URL en `acom/urls.py`. API: `GET /api/v1/mis-inscripciones/<id>/constancia/` devuelve los datos en JSON. **Extra opcional:** exportar a PDF. |

**📅 Actividades diarias (días 1-8, equipo independiente):**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño: qué campos lleva la constancia, bocetar la plantilla en papel | Ficha de diseño |
| 2 | Dominio: `puede_ver_constancia()` + pruebas (reutilizar `generar_folio`) | `test_domain.py` en verde |
| 3-4 | Infraestructura: campos `area_responsable`/`horas_acreditadas` en `Constancia` (con *defaults*), migración, selector `constancia_de()` | `migrate` corre sin error |
| 5-6 | Aplicación: `emitir_constancia` llena los campos nuevos; `obtener_constancia()` autoriza con la regla del dominio | Prueba de servicio en verde |
| 7 | Presentación: plantilla `constancia.html` + URL; endpoint API JSON | Constancia visible en navegador y en Swagger |
| 8 | `git pull origin main`, pruebas finales, PR | PR abierto |

**🎯 Meta del equipo:**
- [ ] La constancia muestra folio, estudiante, actividad, campo, horas, créditos, fecha y responsable
- [ ] El estudiante dueño y el responsable pueden verla
- [ ] Cualquier otro usuario recibe `403`
- [ ] (Opcional) exportación a PDF

**Aceptación (lo que se revisa al cerrar):** el estudiante dueño y el responsable ven la constancia; cualquier otro usuario recibe `403`.

---

### E7 — Kárdex y avance por campo · *Oleada 2 (depende de E1 y E3)*

**Lineamiento:** se necesitan 5 créditos durante la carrera, con formación variada entre campos.

| Capa | Cambios |
|---|---|
| Infraestructura | Selector `avance_por_campo(estudiante) -> dict[campo, Decimal]` (una sola consulta con `values(...).annotate(Sum(...))`). Selector `estudiantes_liberables()` para el departamento. |
| Dominio | Regla pura `puede_liberar(total, por_campo) -> bool`: total ≥ `META_CREDITOS` y ningún campo por encima de `MAX_CREDITOS_POR_CAMPO`. |
| Aplicación | Caso de uso `kardex(estudiante)` que junte total, faltantes, desglose y si puede liberar. |
| Presentación | HTML: vista de kárdex del estudiante. API: **ampliar** `GET /api/v1/mis-inscripciones/resumen/` con `por_campo` y `liberado` (se agregan campos a `ResumenCreditosSerializer` y los actuales se quedan). `GET /api/v1/departamento/liberables/` con `PuedeValidarCreditos`. |

**📅 Actividades diarias:**

| Día | Actividad | Entregable del día |
|---|---|---|
| 1 | Diseño: qué debe mostrar el kárdex (desglose por campo + total + liberado) | Ficha de diseño |
| 2-7 | Preparar `avance_por_campo()` y la regla pura `puede_liberar()` con pruebas usando datos de ejemplo (no requiere que E1/E3 estén mezclados para escribir el código) | `test_domain.py` en verde |
| 8 | `git pull origin main` (ya con E1 y E3 integrados); conectar los selectores reales, ampliar `ResumenCreditosSerializer` | Selector probado contra datos reales |
| 9 | Endpoint `GET /api/v1/departamento/liberables/`, pruebas finales, último PR en mezclarse | PR abierto |

**🎯 Meta del equipo:**
- [ ] El resumen de créditos muestra los 6 campos, incluidos los que están en 0
- [ ] `liberado` pasa a `true` solo al llegar a 5 créditos Y respetando el límite por campo
- [ ] El departamento puede ver la lista de estudiantes liberables

**Aceptación (lo que se revisa al cerrar):** el resumen muestra los 6 campos (incluidos los que están en 0) y `liberado` pasa a `true` al llegar a 5 créditos válidos.

---

## 4. Coordinación

### Dependencias y orden de merge

```
Oleada 1 (días 1–5):   E1 ──┐        E2 ──┐        E5, E6 (en paralelo, archivos propios)
                            │             │
Oleada 2 (días 6–9):   E3 ◄─┘        E4 ◄─┘
                        │
                       E7 ◄── E1 + E3
```

**Orden de merge a `main`:** E1 → E2 → E5 → E6 → E3 → E4 → E7.
E5 y E6 empiezan desde el día 1, pero se integran después de E1/E2 porque tocan los mismos modelos.

### Ramas y PR

- Rama por equipo: `equipo-1/catalogo-campos`, `equipo-2/horas-creditos`, …, `equipo-7/kardex`.
- Un PR por equipo hacia `main`, **revisado por otro equipo** (rotación: E1 revisa E2, E2 revisa E3, …, E7 revisa E1).
- Requisito de merge: pruebas y ruff en verde, y Swagger actualizado.

### Migraciones (riesgo principal)

1. Trabajen sin migración mientras diseñan; generen la suya **justo antes de abrir el PR**, después de `git pull origin main`.
2. Nunca editen una migración de otro equipo.
3. Si al integrar hay conflicto (dos migraciones `0002_...`), **borren la suya y regenérenla** sobre `main`: `uv run python manage.py makemigrations acom`.
4. Las migraciones de datos (E1) van en un archivo propio, no mezcladas con cambios de esquema.

---

## 5. Calendario

| Día | Actividad | Entregable |
|---|---|---|
| 1 | Leer el lineamiento y el README; cada equipo diseña su cambio por capa | Ficha de diseño (1 página) con la regla del lineamiento que implementa |
| 2–4 | Oleada 1: E1 y E2 implementan; E5 y E6 avanzan en dominio, servicios y pruebas | Pruebas de dominio en verde |
| 5 | Merge de E1 y E2; revisión cruzada | `main` con catálogo y horas |
| 6–8 | Oleada 2: E3, E4 y E7 sobre el `main` nuevo; E5 y E6 se integran | PRs abiertos |
| 9 | Integración: merges en orden, suite completa en verde, prueba manual en `/acom/` y `/api/docs/` | `main` estable |
| 10 | Demo de 10 minutos por equipo (misma dinámica del README) | Presentación + prueba en vivo |

---

## 6. Evaluación

| Criterio | Peso | Qué se revisa |
|---|---|---|
| Cumple el lineamiento | 25 % | La regla implementada coincide con el documento del TecNM y la ficha la cita |
| Respeta las capas | 25 % | Dominio sin Django, permisos en `permisos.py`, lecturas en `selectors.py`, errores como `AcomError` |
| Pruebas | 20 % | Dominio sin BD + servicio + API con JWT; la suite completa sigue en verde |
| API y documentación | 15 % | Endpoint visible y usable en Swagger, cambios aditivos en v1 |
| Trabajo en equipo | 15 % | PR limpio, revisión cruzada útil, sin romper el trabajo de otros equipos |

---

## 7. Cómo probar cada funcionalidad en Swagger

1. `uv run python manage.py runserver` y abrir `http://127.0.0.1:8000/api/docs/`.
2. `POST /api/v1/auth/token/` con su usuario → copiar `access`.
3. **Authorize** → pegar el token (sin `Bearer `).
4. Probar sus endpoints con usuarios de cada rol: estudiante, responsable y departamento con permiso *Puede validar constancias y registrar créditos*.
