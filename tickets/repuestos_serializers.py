"""
Serializers relacionados con repuestos.
RF7: El sistema debe permitir al Técnico registrar las piezas o repuestos cambiados.
"""
from rest_framework import serializers
from .repuestos_models import Repuesto


class RepuestoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Repuesto.
    RF7: Permite registrar repuestos utilizados en reparaciones.
    """
    ticket_id = serializers.IntegerField(source='ticket.id', read_only=True)
    registrado_por_nombre = serializers.CharField(source='registrado_por.get_full_name', read_only=True)
    registrado_por_documento = serializers.CharField(source='registrado_por.document', read_only=True)
    costo_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Repuesto
        fields = [
            'id',
            'ticket',
            'ticket_id',
            'nombre',
            'serial',
            'ean',
            'fecha_registro',
            'costo',
            'cantidad',
            'costo_total',
            'registrado_por',
            'registrado_por_nombre',
            'registrado_por_documento',
            'creado_en',
            'actualizado_en'
        ]
        read_only_fields = ['id', 'registrado_por', 'creado_en', 'actualizado_en', 'costo_total']
    
    def validate_costo(self, value):
        """Valida que el costo sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El costo debe ser mayor a cero.")
        return value
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value


class RepuestoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear repuestos.
    El ticket se obtiene de la URL, no del body.
    """
    class Meta:
        model = Repuesto
        fields = [
            'nombre',
            'serial',
            'ean',
            'fecha_registro',
            'costo',
            'cantidad'
        ]
    
    def validate_costo(self, value):
        """Valida que el costo sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El costo debe ser mayor a cero.")
        return value
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value

