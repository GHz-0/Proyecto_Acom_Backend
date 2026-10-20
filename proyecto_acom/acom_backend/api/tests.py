from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APITestCase

from acom.domain.estados import EstadoInscripcion
from acom.models import ActividadComplementaria, CategoriaActividad

User = get_user_model()


class ApiAcomTestCase(APITestCase):
    """Flujo completo de la API: autenticación JWT + inscripción → evaluación →
    constancia → validación, cada paso autenticado como el rol que le corresponde."""

    def setUp(self):
        self.estudiante = User.objects.create_user("estudiante1", password="clave-segura-1")
        self.responsable = User.objects.create_user("docente1", password="clave-segura-1")
        self.depto = User.objects.create_user("depto1", password="clave-segura-1")
        self.depto.user_permissions.add(Permission.objects.get(codename="can_validate_credits"))
        self.actividad = ActividadComplementaria.objects.create(
            nombre="Verano de Investigación",
            categoria=CategoriaActividad.INVESTIGACION,
            responsable=self.responsable,
            creditos_valor=Decimal("2.00"),
        )

    def autenticar_con_jwt(self, username, password="clave-segura-1"):
        """Verifica el endpoint real de login JWT y deja el token listo para lo siguiente."""
        respuesta = self.client.post(
            reverse("api:token_obtain"),
            {"username": username, "password": password},
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertIn("access", respuesta.data)
        token = respuesta.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def test_endpoint_sin_autenticar_devuelve_401(self):
        respuesta = self.client.get(reverse("api:actividades"))
        self.assertEqual(respuesta.status_code, 401)

    def test_login_jwt_y_listar_actividades(self):
        self.autenticar_con_jwt("estudiante1")
        respuesta = self.client.get(reverse("api:actividades"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]["nombre"], "Verano de Investigación")

    def test_flujo_completo_inscripcion_hasta_creditos_validados(self):
        # 1. El estudiante se inscribe
        self.autenticar_con_jwt("estudiante1")
        respuesta = self.client.post(
            reverse(
                "api:inscribirse",
                kwargs={"actividad_id": self.actividad.id},
            )
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        inscripcion_id = respuesta.data["id"]
        self.assertEqual(respuesta.data["estado"], EstadoInscripcion.INSCRITO)

        # inscribirse dos veces debe fallar con 400 (InscripcionDuplicadaError)
        respuesta_dup = self.client.post(
            reverse(
                "api:inscribirse",
                kwargs={"actividad_id": self.actividad.id},
            )
        )
        self.assertEqual(respuesta_dup.status_code, 400)

        # el resumen de créditos debe reflejar 0 mientras no se valide nada
        respuesta_resumen = self.client.get(
            reverse("api:resumen_creditos")
        )
        self.assertEqual(Decimal(respuesta_resumen.data["creditos_totales"]), Decimal("0.00"))

        # 2. El responsable evalúa (aprueba)
        self.autenticar_con_jwt("docente1")
        respuesta = self.client.post(
            reverse(
                "api:evaluar_inscripcion",
                kwargs={"inscripcion_id": inscripcion_id},
            ),
            {"aprobado": True, "observaciones": "Excelente desempeño"},
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertEqual(respuesta.data["estado"], EstadoInscripcion.EVALUADO_APROBADO)

        # 3. El responsable emite la constancia
        respuesta = self.client.post(
            reverse(
                "api:emitir_constancia",
                kwargs={"inscripcion_id": inscripcion_id},
            )
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.assertTrue(respuesta.data["folio"].startswith("ACOM-"))

        # un estudiante intentando emitir la constancia debe recibir 403 (no es el responsable)
        self.autenticar_con_jwt("estudiante1")
        respuesta_prohibida = self.client.post(
            reverse(
                "api:emitir_constancia",
                kwargs={"inscripcion_id": inscripcion_id},
            )
        )
        self.assertEqual(respuesta_prohibida.status_code, 403)

        # 4. Departamento valida y registra los créditos
        self.autenticar_con_jwt("depto1")
        respuesta = self.client.post(
            reverse(
                "api:validar_creditos",
                kwargs={"inscripcion_id": inscripcion_id},
            )
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.assertEqual(Decimal(respuesta.data["creditos_otorgados"]), Decimal("2.00"))

        # un usuario sin el permiso de departamento recibe 403, no 500
        self.autenticar_con_jwt("estudiante1")
        respuesta_sin_permiso = self.client.post(
            reverse(
                "api:validar_creditos",
                kwargs={"inscripcion_id": inscripcion_id},
            )
        )
        self.assertEqual(respuesta_sin_permiso.status_code, 403)

        # 5. El resumen de créditos del estudiante ya refleja los 2.00 otorgados
        self.autenticar_con_jwt("estudiante1")
        respuesta_resumen = self.client.get(
            reverse("api:resumen_creditos")
        )
        self.assertEqual(Decimal(respuesta_resumen.data["creditos_totales"]), Decimal("2.00"))
        self.assertEqual(Decimal(respuesta_resumen.data["creditos_faltantes"]), Decimal("3.00"))


class ApiSchemaTestCase(APITestCase):
    """Confirma que el esquema OpenAPI y las páginas de documentación responden 200."""

    def test_schema_openapi_disponible(self):
        respuesta = self.client.get("/api/schema/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"openapi", respuesta.content)

    def test_swagger_ui_disponible(self):
        respuesta = self.client.get("/api/docs/")
        self.assertEqual(respuesta.status_code, 200)

    def test_redoc_disponible(self):
        respuesta = self.client.get("/api/redoc/")
        self.assertEqual(respuesta.status_code, 200)
