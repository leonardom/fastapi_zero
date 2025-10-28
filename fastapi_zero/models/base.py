from pydantic import BaseModel
from sqlalchemy.orm import registry

table_registry = registry()
Base = table_registry.generate_base()


class ModelBase:
    def update_fields(self, input: BaseModel) -> None:
        """Update fields from a Pydantic model or similar with
        `model_dump(exclude_unset=True)`."""
        for field, value in input.model_dump(exclude_unset=True).items():
            if hasattr(self, field):
                setattr(self, field, value)
