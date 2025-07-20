"""
Base repository class with generic CRUD operations and async support
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import and_, asc, delete, desc, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger
from ..models.base import BaseModel

logger = get_logger(__name__)

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class PaginationParams:
    """Pagination parameters for queries"""

    def __init__(
        self,
        page: int = 1,
        limit: int = 50,
        max_limit: int = 1000
    ):
        self.page = max(1, page)
        self.limit = min(max(1, limit), max_limit)
        self.offset = (self.page - 1) * self.limit


class SortParams:
    """Sorting parameters for queries"""

    def __init__(
        self,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()

    def is_descending(self) -> bool:
        return self.sort_order in ("desc", "descending")


class FilterParams:
    """Base filter parameters"""

    def __init__(self, **filters):
        self.filters = {k: v for k, v in filters.items() if v is not None}


class RepositoryError(Exception):
    """Base repository exception"""
    pass


class NotFoundError(RepositoryError):
    """Entity not found exception"""
    pass


class ValidationError(RepositoryError):
    """Validation error exception"""
    pass


class BaseRepository(Generic[ModelType], ABC):
    """
    Base repository with generic CRUD operations and async support.
    Provides common database operations with proper error handling,
    logging, and performance optimization.
    """

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model
        self.model_name = model.__name__

    @property
    def logger(self):
        """Get logger with context"""
        return logger.bind(model=self.model_name)

    # Core CRUD Operations

    async def create(
        self,
        obj_data: CreateSchemaType | dict[str, Any],
        commit: bool = True
    ) -> ModelType:
        """
        Create a new entity
        
        Args:
            obj_data: Data for creating the entity
            commit: Whether to commit the transaction
            
        Returns:
            Created entity
            
        Raises:
            ValidationError: If data validation fails
            RepositoryError: If creation fails
        """
        try:
            # Convert to dict if needed
            if hasattr(obj_data, 'model_dump'):
                data = obj_data.model_dump(exclude_unset=True)
            elif hasattr(obj_data, 'dict'):
                data = obj_data.dict(exclude_unset=True)
            else:
                data = obj_data

            # Create entity
            db_obj = self.model(**data)
            db_obj.set_creation_audit()

            self.session.add(db_obj)

            if commit:
                await self.session.commit()
                await self.session.refresh(db_obj)

            self.logger.info("Entity created", entity_id=db_obj.id)
            return db_obj

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to create entity", error=str(e))
            raise RepositoryError(f"Failed to create {self.model_name}: {str(e)}")

    async def get_by_id(
        self,
        entity_id: UUID,
        load_relationships: list[str] | None = None
    ) -> ModelType | None:
        """
        Get entity by ID
        
        Args:
            entity_id: Entity UUID
            load_relationships: List of relationships to eager load
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            query = select(self.model).where(self.model.id == entity_id)

            # Add eager loading if specified
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))

            result = await self.session.execute(query)
            entity = result.scalar_one_or_none()

            if entity:
                self.logger.debug("Entity retrieved", entity_id=entity_id)
            else:
                self.logger.debug("Entity not found", entity_id=entity_id)

            return entity

        except SQLAlchemyError as e:
            self.logger.error("Failed to get entity by ID", entity_id=entity_id, error=str(e))
            raise RepositoryError(f"Failed to get {self.model_name} by ID: {str(e)}")

    async def get_by_id_or_raise(
        self,
        entity_id: UUID,
        load_relationships: list[str] | None = None
    ) -> ModelType:
        """
        Get entity by ID or raise NotFoundError
        
        Args:
            entity_id: Entity UUID
            load_relationships: List of relationships to eager load
            
        Returns:
            Entity
            
        Raises:
            NotFoundError: If entity not found
        """
        entity = await self.get_by_id(entity_id, load_relationships)
        if not entity:
            raise NotFoundError(f"{self.model_name} with ID {entity_id} not found")
        return entity

    async def update(
        self,
        entity_id: UUID,
        obj_data: UpdateSchemaType | dict[str, Any],
        commit: bool = True
    ) -> ModelType:
        """
        Update entity by ID
        
        Args:
            entity_id: Entity UUID
            obj_data: Update data
            commit: Whether to commit the transaction
            
        Returns:
            Updated entity
            
        Raises:
            NotFoundError: If entity not found
            RepositoryError: If update fails
        """
        try:
            # Get existing entity
            entity = await self.get_by_id_or_raise(entity_id)

            # Convert to dict if needed
            if hasattr(obj_data, 'model_dump'):
                data = obj_data.model_dump(exclude_unset=True)
            elif hasattr(obj_data, 'dict'):
                data = obj_data.dict(exclude_unset=True)
            else:
                data = obj_data

            # Update entity
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            entity.update_audit_fields()

            if commit:
                await self.session.commit()
                await self.session.refresh(entity)

            self.logger.info("Entity updated", entity_id=entity_id)
            return entity

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to update entity", entity_id=entity_id, error=str(e))
            raise RepositoryError(f"Failed to update {self.model_name}: {str(e)}")

    async def delete(self, entity_id: UUID, commit: bool = True) -> bool:
        """
        Delete entity by ID
        
        Args:
            entity_id: Entity UUID
            commit: Whether to commit the transaction
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        try:
            # Check if entity exists
            entity = await self.get_by_id(entity_id)
            if not entity:
                self.logger.debug("Entity not found for deletion", entity_id=entity_id)
                return False

            # Delete entity
            await self.session.delete(entity)

            if commit:
                await self.session.commit()

            self.logger.info("Entity deleted", entity_id=entity_id)
            return True

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to delete entity", entity_id=entity_id, error=str(e))
            raise RepositoryError(f"Failed to delete {self.model_name}: {str(e)}")

    async def delete_by_filter(
        self,
        filters: dict[str, Any],
        commit: bool = True
    ) -> int:
        """
        Delete entities by filter
        
        Args:
            filters: Filter conditions
            commit: Whether to commit the transaction
            
        Returns:
            Number of deleted entities
        """
        try:
            query = delete(self.model)

            # Apply filters
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            deleted_count = result.rowcount

            if commit:
                await self.session.commit()

            self.logger.info("Entities deleted by filter", count=deleted_count, filters=filters)
            return deleted_count

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to delete entities by filter", filters=filters, error=str(e))
            raise RepositoryError(f"Failed to delete {self.model_name} by filter: {str(e)}")

    # Query Operations

    async def get_all(
        self,
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[ModelType]:
        """
        Get all entities with optional pagination and sorting
        
        Args:
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of entities
        """
        try:
            query = select(self.model)

            # Add sorting
            if sort:
                if hasattr(self.model, sort.sort_by):
                    sort_column = getattr(self.model, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))

            result = await self.session.execute(query)
            entities = result.scalars().all()

            self.logger.debug("Retrieved entities", count=len(entities))
            return list(entities)

        except SQLAlchemyError as e:
            self.logger.error("Failed to get all entities", error=str(e))
            raise RepositoryError(f"Failed to get all {self.model_name}: {str(e)}")

    async def get_by_filter(
        self,
        filters: dict[str, Any],
        pagination: PaginationParams | None = None,
        sort: SortParams | None = None,
        load_relationships: list[str] | None = None
    ) -> list[ModelType]:
        """
        Get entities by filter conditions
        
        Args:
            filters: Filter conditions
            pagination: Pagination parameters
            sort: Sort parameters
            load_relationships: List of relationships to eager load
            
        Returns:
            List of entities matching filters
        """
        try:
            query = select(self.model)

            # Apply filters
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, (list, tuple)):
                        conditions.append(getattr(self.model, key).in_(value))
                    else:
                        conditions.append(getattr(self.model, key) == value)

            if conditions:
                query = query.where(and_(*conditions))

            # Add sorting
            if sort:
                if hasattr(self.model, sort.sort_by):
                    sort_column = getattr(self.model, sort.sort_by)
                    if sort.is_descending():
                        query = query.order_by(desc(sort_column))
                    else:
                        query = query.order_by(asc(sort_column))

            # Add pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.limit)

            # Add eager loading
            if load_relationships:
                for relationship in load_relationships:
                    if hasattr(self.model, relationship):
                        query = query.options(selectinload(getattr(self.model, relationship)))

            result = await self.session.execute(query)
            entities = result.scalars().all()

            self.logger.debug("Retrieved entities by filter", count=len(entities), filters=filters)
            return list(entities)

        except SQLAlchemyError as e:
            self.logger.error("Failed to get entities by filter", filters=filters, error=str(e))
            raise RepositoryError(f"Failed to get {self.model_name} by filter: {str(e)}")

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count entities with optional filters
        
        Args:
            filters: Optional filter conditions
            
        Returns:
            Count of entities
        """
        try:
            query = select(func.count(self.model.id))

            # Apply filters
            if filters:
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, (list, tuple)):
                            conditions.append(getattr(self.model, key).in_(value))
                        else:
                            conditions.append(getattr(self.model, key) == value)

                if conditions:
                    query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            count = result.scalar()

            self.logger.debug("Counted entities", count=count, filters=filters)
            return count

        except SQLAlchemyError as e:
            self.logger.error("Failed to count entities", filters=filters, error=str(e))
            raise RepositoryError(f"Failed to count {self.model_name}: {str(e)}")

    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if entity exists by ID
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            query = select(func.count(self.model.id)).where(self.model.id == entity_id)
            result = await self.session.execute(query)
            count = result.scalar()

            exists = count > 0
            self.logger.debug("Checked entity existence", entity_id=entity_id, exists=exists)
            return exists

        except SQLAlchemyError as e:
            self.logger.error("Failed to check entity existence", entity_id=entity_id, error=str(e))
            raise RepositoryError(f"Failed to check {self.model_name} existence: {str(e)}")

    # Bulk Operations

    async def bulk_create(
        self,
        objects_data: list[CreateSchemaType | dict[str, Any]],
        commit: bool = True
    ) -> list[ModelType]:
        """
        Bulk create entities
        
        Args:
            objects_data: List of entity data
            commit: Whether to commit the transaction
            
        Returns:
            List of created entities
        """
        try:
            db_objects = []

            for obj_data in objects_data:
                # Convert to dict if needed
                if hasattr(obj_data, 'model_dump'):
                    data = obj_data.model_dump(exclude_unset=True)
                elif hasattr(obj_data, 'dict'):
                    data = obj_data.dict(exclude_unset=True)
                else:
                    data = obj_data

                db_obj = self.model(**data)
                db_obj.set_creation_audit()
                db_objects.append(db_obj)

            self.session.add_all(db_objects)

            if commit:
                await self.session.commit()
                # Refresh all objects to get IDs
                for obj in db_objects:
                    await self.session.refresh(obj)

            self.logger.info("Bulk entities created", count=len(db_objects))
            return db_objects

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to bulk create entities", count=len(objects_data), error=str(e))
            raise RepositoryError(f"Failed to bulk create {self.model_name}: {str(e)}")

    async def bulk_update(
        self,
        updates: list[dict[str, Any]],
        commit: bool = True
    ) -> int:
        """
        Bulk update entities
        
        Args:
            updates: List of update data with 'id' field
            commit: Whether to commit the transaction
            
        Returns:
            Number of updated entities
        """
        try:
            updated_count = 0

            for update_data in updates:
                if 'id' not in update_data:
                    continue

                entity_id = update_data.pop('id')

                # Add audit field
                update_data['updated_at'] = datetime.utcnow()

                query = update(self.model).where(self.model.id == entity_id).values(**update_data)
                result = await self.session.execute(query)
                updated_count += result.rowcount

            if commit:
                await self.session.commit()

            self.logger.info("Bulk entities updated", count=updated_count)
            return updated_count

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to bulk update entities", error=str(e))
            raise RepositoryError(f"Failed to bulk update {self.model_name}: {str(e)}")

    # Transaction Management

    async def save(self, entity: ModelType, commit: bool = True) -> ModelType:
        """
        Save entity (add to session and optionally commit)
        
        Args:
            entity: Entity to save
            commit: Whether to commit the transaction
            
        Returns:
            Saved entity
        """
        try:
            self.session.add(entity)

            if commit:
                await self.session.commit()
                await self.session.refresh(entity)

            self.logger.debug("Entity saved", entity_id=entity.id)
            return entity

        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Failed to save entity", entity_id=getattr(entity, 'id', None), error=str(e))
            raise RepositoryError(f"Failed to save {self.model_name}: {str(e)}")

    # Abstract methods for model-specific operations

    @abstractmethod
    async def get_by_unique_field(self, field_name: str, field_value: Any) -> ModelType | None:
        """Get entity by unique field - to be implemented by specific repositories"""
        pass
