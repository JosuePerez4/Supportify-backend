"""
Modelos relacionados con repuestos.
RF7: El sistema debe permitir al Técnico registrar las piezas o repuestos cambiados.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
# Importación diferida para evitar importación circular
from django.db import models


class Repuesto(models.Model):
    """
    Modelo para registrar repuestos o piezas utilizadas en la reparación de tickets.
    RF7: El sistema debe permitir al Técnico registrar las piezas o repuestos cambiados.
    """
    ticket = models.ForeignKey(
        'tickets.Ticket',  # Usar string para evitar importación circular
        on_delete=models.CASCADE,
        related_name='repuestos_registrados',
        help_text="Ticket al que pertenece este repuesto"
    )
    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del repuesto o pieza"
    )
    serial = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Número de serie del repuesto (opcional)"
    )
    ean = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Código EAN del repuesto (opcional)"
    )
    fecha_registro = models.DateField(
        default=timezone.now,
        help_text="Fecha en que se registró el repuesto"
    )
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Costo del repuesto"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de repuestos utilizados"
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repuestos_registrados',
        help_text="Técnico que registró el repuesto"
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ['-fecha_registro', '-creado_en']
        indexes = [
            models.Index(fields=['ticket', '-fecha_registro']),
        ]

    def __str__(self):
        return f"{self.nombre} - Ticket #{self.ticket.pk}"

    @property
    def costo_total(self):
        """Calcula el costo total (costo unitario * cantidad)"""
        return self.costo * self.cantidad

