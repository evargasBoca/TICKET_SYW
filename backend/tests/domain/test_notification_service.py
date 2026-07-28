"""NotificationService — evento 'reassigned' y mensaje enriquecido (OBS-0046)."""
import uuid

from backend.domain.services.notification_service import NotificationService


def test_build_reassigned_includes_ticket_number():
    notif = NotificationService().build(
        uuid.uuid4(), "reassigned", uuid.uuid4(), 3, "Ticket QA prueba")
    assert notif.event_type == "reassigned"
    assert "TK-000003" in notif.message


def test_build_assigned_enriched_message_includes_details():
    notif = NotificationService().build(
        uuid.uuid4(), "assigned", uuid.uuid4(), 3, "Ticket QA prueba",
        client_name="Cliente QA", priority="high", status="contacto", assigned_by="admin")
    assert "Cliente: Cliente QA" in notif.message
    assert "Prioridad: high" in notif.message
    assert "Estado: Contacto" in notif.message
    assert "Asignado por: admin" in notif.message


def test_build_reassigned_without_details_keeps_base_message():
    notif = NotificationService().build(uuid.uuid4(), "reassigned", uuid.uuid4(), 3, "t")
    assert notif.message == "Se te reasignó el ticket TK-000003: t"
