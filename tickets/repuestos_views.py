"""
Vistas relacionadas con repuestos.
RF7: El sistema debe permitir al Técnico registrar las piezas o repuestos cambiados.
"""
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from tickets.permissions import IsTechnician
from tickets.models import Ticket
from tickets.repuestos_models import Repuesto
from tickets.repuestos_serializers import RepuestoSerializer, RepuestoCreateSerializer
from tickets.models import TicketHistory

User = get_user_model()


class RepuestoListCreateAV(ListCreateAPIView):
    """
    Vista para que los técnicos registren repuestos en un ticket.
    RF7: Permite al técnico registrar piezas o repuestos cambiados en cada reparación.
    """
    permission_classes = [IsTechnician]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepuestoCreateSerializer
        return RepuestoSerializer
    
    def get_queryset(self):
        """
        Retorna los repuestos del ticket especificado.
        Solo el técnico asignado al ticket puede ver sus repuestos.
        """
        ticket_id = self.kwargs.get('ticket_id')
        user = self.request.user
        
        if not user or not user.is_authenticated or user.role != User.Role.TECH:
            return Repuesto.objects.none()
        
        # Verificar que el ticket existe y pertenece al técnico
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        
        # Solo el técnico asignado puede ver/crear repuestos
        if ticket.tecnico != user:
            return Repuesto.objects.none()
        
        return Repuesto.objects.filter(ticket=ticket).select_related('registrado_por', 'ticket')
    
    def perform_create(self, serializer):
        """
        Crea un nuevo repuesto asociado al ticket.
        El técnico autenticado se asigna automáticamente como registrado_por.
        """
        ticket_id = self.kwargs.get('ticket_id')
        user = self.request.user
        
        # Validar que el ticket existe y pertenece al técnico
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        
        if ticket.tecnico != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Solo el técnico asignado al ticket puede registrar repuestos.')
        
        # Validar que el ticket no esté finalizado
        if ticket.estado and ticket.estado.es_final:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('No se pueden registrar repuestos en un ticket finalizado.')
        
        # Crear el repuesto
        repuesto = serializer.save(
            ticket=ticket,
            registrado_por=user
        )
        
        # Registrar en el historial del ticket
        TicketHistory.crear_entrada_historial(
            ticket=ticket,
            accion=f"Repuesto registrado: {repuesto.nombre} (Cantidad: {repuesto.cantidad}, Costo: ${repuesto.costo})",
            realizado_por=user,
            estado_anterior=None
        )
        
        return repuesto
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos los repuestos del ticket.
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': 'No hay repuestos registrados para este ticket.',
                'repuestos': [],
                'total_costo': 0
            }, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Calcular el costo total de todos los repuestos
        costo_total = sum(repuesto.costo_total for repuesto in queryset)
        
        return Response({
            'message': 'Repuestos obtenidos exitosamente',
            'ticket_id': self.kwargs.get('ticket_id'),
            'total_repuestos': queryset.count(),
            'total_costo': float(costo_total),
            'repuestos': serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo repuesto para el ticket.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        repuesto = self.perform_create(serializer)
        
        # Serializar el repuesto creado con todos los campos
        repuesto_serializer = RepuestoSerializer(repuesto)
        
        return Response({
            'message': 'Repuesto registrado exitosamente',
            'repuesto': repuesto_serializer.data
        }, status=status.HTTP_201_CREATED)


class RepuestoDetailAV(RetrieveUpdateDestroyAPIView):
    """
    Vista para ver, actualizar o eliminar un repuesto específico.
    RF7: Permite al técnico gestionar repuestos registrados.
    """
    serializer_class = RepuestoSerializer
    permission_classes = [IsTechnician]
    
    def get_queryset(self):
        """
        Retorna el repuesto específico.
        Solo el técnico asignado al ticket puede gestionar sus repuestos.
        """
        repuesto_id = self.kwargs.get('repuesto_id')
        user = self.request.user
        
        if not user or not user.is_authenticated or user.role != User.Role.TECH:
            return Repuesto.objects.none()
        
        repuesto = get_object_or_404(Repuesto, pk=repuesto_id)
        
        # Solo el técnico asignado al ticket puede gestionar repuestos
        if repuesto.ticket.tecnico != user:
            return Repuesto.objects.none()
        
        return Repuesto.objects.filter(pk=repuesto_id).select_related('registrado_por', 'ticket')
    
    def get_object(self):
        """
        Obtiene el repuesto y valida permisos.
        """
        repuesto = super().get_object()
        
        # Validar que el ticket no esté finalizado (para update/delete)
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if repuesto.ticket.estado and repuesto.ticket.estado.es_final:
                from rest_framework.exceptions import ValidationError
                raise ValidationError('No se pueden modificar repuestos de un ticket finalizado.')
        
        return repuesto
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un repuesto existente.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        repuesto = serializer.save()
        
        # Registrar en el historial del ticket
        TicketHistory.crear_entrada_historial(
            ticket=repuesto.ticket,
            accion=f"Repuesto actualizado: {repuesto.nombre} (Cantidad: {repuesto.cantidad}, Costo: ${repuesto.costo})",
            realizado_por=request.user,
            estado_anterior=None
        )
        
        return Response({
            'message': 'Repuesto actualizado exitosamente',
            'repuesto': serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un repuesto.
        """
        instance = self.get_object()
        ticket = instance.ticket
        nombre_repuesto = instance.nombre
        
        instance.delete()
        
        # Registrar en el historial del ticket
        TicketHistory.crear_entrada_historial(
            ticket=ticket,
            accion=f"Repuesto eliminado: {nombre_repuesto}",
            realizado_por=request.user,
            estado_anterior=None
        )
        
        return Response({
            'message': 'Repuesto eliminado exitosamente'
        }, status=status.HTTP_200_OK)

