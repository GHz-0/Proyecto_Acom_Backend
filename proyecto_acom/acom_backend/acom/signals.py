"""Observer: el servicio avisa que algo pasó sin saber quién reacciona."""

import django.dispatch

inscripcion_validada = django.dispatch.Signal()
