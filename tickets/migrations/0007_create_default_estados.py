# Generated manually to ensure estados are created in production

from django.db import migrations


def create_default_estados(apps, schema_editor):
    """
    Crea los estados por defecto si no existen.
    Esto asegura que los estados estén disponibles incluso si los fixtures no se cargaron.
    """
    Estado = apps.get_model('tickets', 'Estado')
    
    estados_default = [
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
    
    for estado_data in estados_default:
        # Intentar obtener por ID primero, luego por código
        estado = None
        try:
            estado = Estado.objects.get(pk=estado_data['id'])
            # Si existe por ID pero el código es diferente, actualizar
            if estado.codigo != estado_data['codigo']:
                estado.codigo = estado_data['codigo']
                estado.nombre = estado_data['nombre']
                estado.es_activo = estado_data['es_activo']
                estado.es_final = estado_data['es_final']
                estado.save()
                print(f"Estado actualizado por ID: {estado_data['id']} - {estado.codigo} - {estado.nombre}")
            else:
                # Actualizar otros campos si es necesario
                estado.nombre = estado_data['nombre']
                estado.es_activo = estado_data['es_activo']
                estado.es_final = estado_data['es_final']
                estado.save()
                print(f"Estado actualizado: {estado.codigo} - {estado.nombre}")
        except Estado.DoesNotExist:
            # Si no existe por ID, intentar por código
            estado, created = Estado.objects.get_or_create(
                codigo=estado_data['codigo'],
                defaults={
                    'nombre': estado_data['nombre'],
                    'es_activo': estado_data['es_activo'],
                    'es_final': estado_data['es_final']
                }
            )
            if created:
                # Si se creó, asegurar que tenga el ID correcto
                if estado.pk != estado_data['id']:
                    # No podemos cambiar el ID directamente, pero podemos actualizar los datos
                    print(f"Estado creado con código {estado.codigo} pero ID diferente ({estado.pk} vs {estado_data['id']})")
                print(f"Estado creado: {estado.codigo} - {estado.nombre}")
            else:
                # Actualizar si ya existe pero con datos diferentes
                estado.nombre = estado_data['nombre']
                estado.es_activo = estado_data['es_activo']
                estado.es_final = estado_data['es_final']
                estado.save()
                print(f"Estado actualizado: {estado.codigo} - {estado.nombre}")


def reverse_migration(apps, schema_editor):
    """
    No revertimos la creación de estados ya que son necesarios para el funcionamiento del sistema.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_merge_0005_remove_estado_6_0005_tickethistory'),
    ]

    operations = [
        migrations.RunPython(
            create_default_estados,
            reverse_migration
        ),
    ]

