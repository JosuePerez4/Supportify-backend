#!/usr/bin/env python
"""
Script para crear 4 usuarios de prueba en producción:
- ADMIN (Administrador)
- TECH (Técnico)
- CLIENT (Cliente)
- OWNER (Dueño)

Credenciales fáciles:
- ADMIN: admin@test.com / admin123
- TECH: tech@test.com / tech123
- CLIENT: client@test.com / client123
- OWNER: owner@test.com / owner123
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tickethelp.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def crear_usuarios():
    """Crea 4 usuarios de prueba, uno de cada tipo"""
    print("=" * 60)
    print("CREACIÓN DE USUARIOS EN PRODUCCIÓN")
    print("=" * 60)
    print()
    
    usuarios_config = [
        {
            'document': '1000000001',
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'Test',
            'number': '3001234567',
            'role': User.Role.ADMIN,
            'password': 'admin123',
            'rol_nombre': 'ADMIN'
        },
        {
            'document': '2000000001',
            'email': 'tech@test.com',
            'first_name': 'Tech',
            'last_name': 'Test',
            'number': '3001234568',
            'role': User.Role.TECH,
            'password': 'tech123',
            'rol_nombre': 'TECH'
        },
        {
            'document': '3000000001',
            'email': 'client@test.com',
            'first_name': 'Client',
            'last_name': 'Test',
            'number': '3001234569',
            'role': User.Role.CLIENT,
            'password': 'client123',
            'rol_nombre': 'CLIENT'
        },
        {
            'document': '4000000001',
            'email': 'owner@test.com',
            'first_name': 'Owner',
            'last_name': 'Test',
            'number': '3001234570',
            'role': User.Role.OWNER,
            'password': 'owner123',
            'rol_nombre': 'OWNER'
        },
    ]
    
    usuarios_creados = []
    usuarios_existentes = []
    
    for config in usuarios_config:
        try:
            # Intentar obtener el usuario si ya existe
            usuario, created = User.objects.get_or_create(
                document=config['document'],
                defaults={
                    'email': config['email'],
                    'first_name': config['first_name'],
                    'last_name': config['last_name'],
                    'number': config['number'],
                    'role': config['role'],
                    'is_active': True,
                    'must_change_password': False,
                }
            )
            
            if created:
                # Establecer contraseña
                usuario.set_password(config['password'])
                usuario.save()
                usuarios_creados.append(usuario)
                print(f"✓ Usuario {config['rol_nombre']} creado:")
                print(f"  - Email: {usuario.email}")
                print(f"  - Documento: {usuario.document}")
                print(f"  - Contraseña: {config['password']}")
                print()
            else:
                # Usuario ya existe, actualizar contraseña y datos
                usuario.email = config['email']
                usuario.first_name = config['first_name']
                usuario.last_name = config['last_name']
                usuario.number = config['number']
                usuario.role = config['role']
                usuario.is_active = True
                usuario.must_change_password = False
                usuario.set_password(config['password'])
                usuario.save()
                usuarios_existentes.append(usuario)
                print(f"→ Usuario {config['rol_nombre']} ya existía, actualizado:")
                print(f"  - Email: {usuario.email}")
                print(f"  - Documento: {usuario.document}")
                print(f"  - Contraseña: {config['password']}")
                print()
                
        except Exception as e:
            print(f"✗ Error al crear usuario {config['rol_nombre']}: {str(e)}")
            print()
    
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Usuarios nuevos creados: {len(usuarios_creados)}")
    print(f"Usuarios existentes actualizados: {len(usuarios_existentes)}")
    print()
    print("CREDENCIALES:")
    print("-" * 60)
    for config in usuarios_config:
        print(f"{config['rol_nombre']:8} | Email: {config['email']:20} | Password: {config['password']}")
    print("=" * 60)
    print()
    print("✓ Proceso completado!")
    print()
    print("NOTA: Estos usuarios tienen must_change_password=False,")
    print("      por lo que pueden iniciar sesión directamente.")
    print("=" * 60)

if __name__ == '__main__':
    try:
        crear_usuarios()
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

