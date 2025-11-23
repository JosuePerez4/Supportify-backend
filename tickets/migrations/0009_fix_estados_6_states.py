# Generated manually to fix estados to 6 states

from django.db import migrations


def fix_estados_6_states(apps, schema_editor):
    """
    Corrige los estados para que sean exactamente 6 según el fixtures.
    Actualiza los estados existentes y crea los que faltan.
    """
    Estado = apps.get_model('tickets', 'Estado')
    
    estados_correctos = [
        {
            'id': 1,
            'codigo': 'open',
            'nombre': 'Abierto',
            'es_activo': True,
            'es_final': False
        },
        {
            'id': 2,
            'codigo': 'diagnosis',
            'nombre': 'En diagnóstico',
            'es_activo': True,
            'es_final': False
        },
        {
            'id': 3,
            'codigo': 'in_repair',
            'nombre': 'En reparación',
            'es_activo': True,
            'es_final': False
        },
        {
            'id': 4,
            'codigo': 'Waiting_for_replacement_parts',
            'nombre': 'Esperando repuestos',
            'es_activo': True,
            'es_final': False
        },
        {
            'id': 5,
            'codigo': 'trial',
            'nombre': 'En prueba',
            'es_activo': True,
            'es_final': False
        },
        {
            'id': 6,
            'codigo': 'closed',
            'nombre': 'finalizado',
            'es_activo': False,
            'es_final': True
        }
    ]
    
    # Primero, corregir estados existentes por ID
    for estado_data in estados_correctos:
        estado_id = estado_data['id']
        try:
            estado = Estado.objects.get(pk=estado_id)
            # Actualizar todos los campos
            estado.codigo = estado_data['codigo']
            estado.nombre = estado_data['nombre']
            estado.es_activo = estado_data['es_activo']
            estado.es_final = estado_data['es_final']
            estado.save()
            print(f"Estado {estado_id} actualizado: {estado.codigo} - {estado.nombre}")
        except Estado.DoesNotExist:
            # Si no existe por ID, crear nuevo
            estado = Estado.objects.create(
                codigo=estado_data['codigo'],
                nombre=estado_data['nombre'],
                es_activo=estado_data['es_activo'],
                es_final=estado_data['es_final']
            )
            print(f"Estado {estado_id} creado: {estado.codigo} - {estado.nombre}")
    
    # Eliminar estados que no deberían existir (códigos incorrectos)
    estados_a_eliminar = ['finalized']  # Este código ya no se usa, ahora es 'closed'
    for codigo_incorrecto in estados_a_eliminar:
        Estado.objects.filter(codigo=codigo_incorrecto).exclude(codigo='closed').delete()
        print(f"Estados con código '{codigo_incorrecto}' eliminados (si existían)")


def reverse_migration(apps, schema_editor):
    """
    No revertimos la corrección de estados ya que son necesarios para el funcionamiento del sistema.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_remove_ticket_titulo_ticket_fecha_estimada_and_more'),
    ]

    operations = [
        migrations.RunPython(
            fix_estados_6_states,
            reverse_migration
        ),
    ]

