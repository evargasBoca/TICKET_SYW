from typing import Optional
import uuid

from sqlalchemy.orm import Session

from backend.infra.models.catalog_model import CATALOG_MODELS, tool_processes_table


class CatalogRepository:
    """Repositorio genérico para los 3 catálogos de tickets (tools/processes/resolution-types)."""

    def __init__(self, db: Session, catalog: str) -> None:
        if catalog not in CATALOG_MODELS:
            raise ValueError(f"Catálogo desconocido: {catalog}")
        self._db = db
        self._model = CATALOG_MODELS[catalog]

    def list_all(self, active: bool | None = True) -> list[dict]:
        q = self._db.query(self._model)
        if active is not None:
            q = q.filter(self._model.active == active)
        return [m.to_dict() for m in q.order_by(self._model.name).all()]

    def get_by_id(self, catalog_id: uuid.UUID) -> Optional[dict]:
        model = self._db.get(self._model, catalog_id)
        return model.to_dict() if model else None

    def get_by_name(self, name: str) -> Optional[dict]:
        model = self._db.query(self._model).filter(self._model.name == name).first()
        return model.to_dict() if model else None

    def create(self, name: str) -> dict:
        kwargs = {"id": uuid.uuid4(), "name": name}
        if hasattr(self._model, "color_index"):
            # research.md Decisión 2: siguiente color libre de una paleta fija de 8 (frontend),
            # nunca elegido por el usuario; estable una vez asignado.
            existing_count = self._db.query(self._model).count()
            kwargs["color_index"] = existing_count % 8
        model = self._model(**kwargs)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return model.to_dict()

    def set_active(self, catalog_id: uuid.UUID, active: bool) -> Optional[dict]:
        model = self._db.get(self._model, catalog_id)
        if not model:
            return None
        model.active = active
        self._db.commit()
        return model.to_dict()

    def rename(self, catalog_id: uuid.UUID, name: str) -> Optional[dict]:
        """spec 035 (US5): renombra un registro existente, preservando su id y referencias."""
        model = self._db.get(self._model, catalog_id)
        if not model:
            return None
        model.name = name
        self._db.commit()
        self._db.refresh(model)
        return model.to_dict()


class ToolProcessRepository:
    """Vínculos sugeridos Herramienta↔Proceso (OBS-0049) — tabla puente `tool_processes`."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self) -> list[dict]:
        rows = self._db.execute(tool_processes_table.select()).all()
        return [{"tool_id": str(r.tool_id), "process_id": str(r.process_id)} for r in rows]

    def link(self, tool_id: uuid.UUID, process_id: uuid.UUID) -> dict:
        exists = self._db.execute(
            tool_processes_table.select().where(
                tool_processes_table.c.tool_id == tool_id,
                tool_processes_table.c.process_id == process_id,
            )
        ).first()
        if not exists:
            self._db.execute(tool_processes_table.insert().values(tool_id=tool_id, process_id=process_id))
            self._db.commit()
        return {"tool_id": str(tool_id), "process_id": str(process_id)}

    def unlink(self, tool_id: uuid.UUID, process_id: uuid.UUID) -> bool:
        result = self._db.execute(
            tool_processes_table.delete().where(
                tool_processes_table.c.tool_id == tool_id,
                tool_processes_table.c.process_id == process_id,
            )
        )
        self._db.commit()
        return result.rowcount > 0
