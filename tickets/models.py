from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
import json


class Estado(models.Model):
    codigo    = models.SlugField(max_length=32, unique=True)
    nombre    = models.CharField(max_length=60, unique=True)
    es_activo = models.BooleanField(default=True)
    es_final  = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# -------------------------------------------------------
#  PRIORIDAD
# -------------------------------------------------------
PRIORIDAD_CHOICES = [
    ('low', 'Baja'),
    ('medium', 'Media'),
    ('high', 'Alta'),
    ('urgent', 'Urgente'),
]


class Ticket(models.Model):
    # Relaciones
    administrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=False,
        on_delete=models.SET_NULL,
        related_name="tickets_administrados",
    )
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=False,
        on_delete=models.SET_NULL,
        related_name="tickets_asignados",
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=False,
        on_delete=models.SET_NULL,
        related_name="tickets_de_cliente",
    )

    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        related_name="tickets",
    )

    # Datos principales del ticket
    descripcion  = models.TextField(blank=True)
    equipo       = models.CharField(max_length=120, blank=True)

    # -------- PRIORIDAD ---------
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default="medium"
    )

    # Fechas
    fecha_estimada = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha estimada ingresada por quien crea el ticket."
    )

    repuestos = models.TextField(
        null=True,
        blank=True,
        help_text="Repuestos utilizados o requeridos (opcional)."
    )

    fecha = models.DateTimeField(default=timezone.now)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["creado_en"]),
        ]
        ordering = ["-creado_en"]

    def __str__(self):
        base = self.equipo if self.equipo else "Ticket sin equipo"
        return f"[#{self.pk}] {base} · {self.estado.nombre}"

    @property
    def es_activo(self) -> bool:
        return bool(getattr(self.estado, "es_activo", False))


class StateChangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='state_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='state_requests_made')
    from_state = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='requests_from')
    to_state = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='requests_to')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_requests_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Solicitud de Cambio de Estado"
        verbose_name_plural = "Solicitudes de Cambio de Estado"

    def __str__(self):
        return f"Solicitud #{self.pk} - Ticket #{self.ticket.pk}: {self.from_state.nombre} → {self.to_state.nombre}"


class TicketHistory(models.Model):
    ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE, related_name='historial')
    estado = models.CharField(max_length=50)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='historiales_como_tecnico')
    tecnico_anterior = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='historiales_como_tecnico_anterior')
    accion = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acciones_realizadas')
    datos_ticket = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Historial de Ticket"
        verbose_name_plural = "Historiales de Tickets"
        indexes = [
            models.Index(fields=['ticket', '-fecha']),
        ]

    def __str__(self):
        return f"Historial #{self.id} - Ticket #{self.ticket.id} - {self.accion} ({self.fecha})"
    
    @staticmethod
    def crear_entrada_historial(ticket, accion, realizado_por, estado_anterior=None, tecnico_anterior=None, datos_ticket=None):

        if datos_ticket is None:
            datos_ticket = {
                'descripcion': ticket.descripcion,
                'equipo': ticket.equipo,
                'prioridad': ticket.prioridad,  # 👈 AÑADIDO
                'fecha_estimada': ticket.fecha_estimada.isoformat() if ticket.fecha_estimada else None,
                'repuestos': ticket.repuestos,
                'administrador': ticket.administrador.document if ticket.administrador else None,
                'cliente': ticket.cliente.document if ticket.cliente else None,
            }
        
        return TicketHistory.objects.create(
            ticket=ticket,
            estado=ticket.estado.nombre if ticket.estado else 'Sin estado',
            estado_anterior=estado_anterior,
            tecnico=ticket.tecnico,
            tecnico_anterior=tecnico_anterior,
            accion=accion,
            realizado_por=realizado_por,
            datos_ticket=datos_ticket
        )


@receiver(pre_save, sender=Ticket)
def store_previous_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            instance._old_estado = old_instance.estado
            instance._old_tecnico = old_instance.tecnico
        except Ticket.DoesNotExist:
            instance._old_estado = None
            instance._old_tecnico = None
    else:
        instance._old_estado = None
        instance._old_tecnico = None
