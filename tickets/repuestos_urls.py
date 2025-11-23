"""
URLs relacionadas con repuestos.
RF7: El sistema debe permitir al Técnico registrar las piezas o repuestos cambiados.
"""
from django.urls import path
from tickets.repuestos_views import RepuestoListCreateAV, RepuestoDetailAV

urlpatterns = [
    # RF7: Endpoints para que técnicos registren repuestos en tickets
    path('tickets/<int:ticket_id>/repuestos/', RepuestoListCreateAV.as_view(), name="repuestos-list-create"),
    path('tickets/<int:ticket_id>/repuestos/<int:repuesto_id>/', RepuestoDetailAV.as_view(), name="repuesto-detail"),
]

