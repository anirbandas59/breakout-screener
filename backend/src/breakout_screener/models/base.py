"""
Base model with common fields and functionality for all models
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from ..core.database import Base


class BaseModel(Base):
    """
    Base model class with common audit fields and functionality.
    All models inherit from this to get consistent audit trail and UUID primary keys.
    """

    __abstract__ = True

    # Primary key as UUID for better distribution and security
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="Unique identifier for the record"
    )

    # Audit fields for tracking record lifecycle
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )

    created_by = Column(
        String(100),
        default="system",
        nullable=False,
        comment="User or system that created the record"
    )

    updated_by = Column(
        String(100),
        default="system",
        nullable=False,
        comment="User or system that last updated the record"
    )

    @declared_attr
    def __tablename__(cls):
        """
        Generate table name from class name.
        CamelCase -> snake_case conversion
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self, exclude_fields: list | None = None) -> dict:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude_fields: List of field names to exclude from output
            
        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or []
        result = {}

        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)

                # Handle datetime serialization
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                # Handle UUID serialization
                elif hasattr(value, '__str__') and str(type(value)).find('UUID') != -1:
                    result[column.name] = str(value)
                # Handle enum serialization
                elif hasattr(value, 'value'):
                    result[column.name] = value.value
                else:
                    result[column.name] = value

        return result

    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model"""
        return cls.__tablename__

    def update_audit_fields(self, user: str = "system") -> None:
        """
        Update audit fields for the record
        
        Args:
            user: Username or system identifier making the change
        """
        now = datetime.now(UTC)
        self.updated_at = now
        self.updated_by = user

    def set_creation_audit(self, user: str = "system") -> None:
        """
        Set creation audit fields for new records
        
        Args:
            user: Username or system identifier creating the record
        """
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
        self.created_by = user
        self.updated_by = user
