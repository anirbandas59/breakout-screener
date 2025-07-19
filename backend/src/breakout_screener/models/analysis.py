"""
Analysis session and performance metrics models
New models for tracking analysis runs and performance data
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from sqlalchemy import (
    Column, String, Integer, DateTime, Text, ForeignKey, Index, 
    CheckConstraint, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, DECIMAL, JSONB
from sqlalchemy.orm import relationship, validates

from .base import BaseModel


class AnalysisSession(BaseModel):
    """
    Track analysis runs and batch processing sessions.
    Provides monitoring and audit trail for breakout analysis operations.
    """
    
    __tablename__ = "analysis_sessions"
    
    # Session identification
    session_name = Column(
        String(255),
        nullable=False,
        comment="Human-readable name for the analysis session"
    )
    
    # Session timing
    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the analysis session started"
    )
    
    end_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the analysis session completed"
    )
    
    # Session status
    status = Column(
        String(20),
        default="RUNNING",
        nullable=False,
        index=True,
        comment="Current status of the analysis session"
    )
    
    # Processing statistics
    total_stocks_processed = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of stocks processed in this session"
    )
    
    successful_analyses = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of successful analysis operations"
    )
    
    failed_analyses = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of failed analysis operations"
    )
    
    # Error tracking
    error_details = Column(
        JSONB,
        nullable=True,
        comment="JSON structure containing error details and stack traces"
    )
    
    # Configuration and metadata
    configuration = Column(
        JSONB,
        nullable=True,
        comment="JSON structure containing session configuration parameters"
    )
    
    # Relationships
    performance_metrics = relationship(
        "PerformanceMetrics",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_analysis_sessions_valid_status"
        ),
        CheckConstraint(
            "total_stocks_processed >= 0",
            name="ck_analysis_sessions_total_stocks_non_negative"
        ),
        CheckConstraint(
            "successful_analyses >= 0",
            name="ck_analysis_sessions_successful_non_negative"
        ),
        CheckConstraint(
            "failed_analyses >= 0",
            name="ck_analysis_sessions_failed_non_negative"
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time",
            name="ck_analysis_sessions_end_after_start"
        ),
        
        Index("idx_analysis_sessions_start_time", "start_time"),
        Index("idx_analysis_sessions_status_start", "status", "start_time"),
        Index("idx_analysis_sessions_session_name", "session_name"),
        
        {"comment": "Tracking table for analysis runs and batch processing"}
    )
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate session status"""
        valid_statuses = ['RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}: {status}")
        return status
    
    @validates('session_name')
    def validate_session_name(self, key, session_name):
        """Validate session name"""
        if not session_name or not session_name.strip():
            raise ValueError("Session name cannot be empty")
        return session_name.strip()
    
    def __repr__(self) -> str:
        return (f"<AnalysisSession(name={self.session_name}, status={self.status}, "
                f"processed={self.total_stocks_processed})>")
    
    def start_session(self, configuration: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark session as started with optional configuration.
        
        Args:
            configuration: Dictionary of configuration parameters
        """
        self.start_time = datetime.utcnow()
        self.status = "RUNNING"
        self.configuration = configuration or {}
        self.total_stocks_processed = 0
        self.successful_analyses = 0
        self.failed_analyses = 0
    
    def complete_session(self, success: bool = True) -> None:
        """
        Mark session as completed.
        
        Args:
            success: Whether the session completed successfully
        """
        self.end_time = datetime.utcnow()
        self.status = "COMPLETED" if success else "FAILED"
    
    def cancel_session(self) -> None:
        """Mark session as cancelled"""
        self.end_time = datetime.utcnow()
        self.status = "CANCELLED"
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Add error information to the session.
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        if self.error_details is None:
            self.error_details = []
        
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.error_details.append(error_entry)
        self.failed_analyses += 1
    
    def increment_success(self) -> None:
        """Increment successful analysis counter"""
        self.successful_analyses += 1
        self.total_stocks_processed += 1
    
    def get_duration_seconds(self) -> Optional[int]:
        """Get session duration in seconds"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None
    
    def get_success_rate(self) -> Optional[float]:
        """Get success rate as percentage"""
        if self.total_stocks_processed > 0:
            return (self.successful_analyses / self.total_stocks_processed) * 100
        return None
    
    def is_running(self) -> bool:
        """Check if session is currently running"""
        return self.status == "RUNNING"
    
    def is_completed(self) -> bool:
        """Check if session completed successfully"""
        return self.status == "COMPLETED"
    
    def to_dict(self, include_metrics: bool = False, exclude_fields: Optional[list] = None) -> dict:
        """
        Convert analysis session to dictionary.
        
        Args:
            include_metrics: Whether to include performance metrics
            exclude_fields: List of fields to exclude
            
        Returns:
            Dictionary representation
        """
        exclude_fields = exclude_fields or []
        result = super().to_dict(exclude_fields)
        
        # Add calculated fields
        result['duration_seconds'] = self.get_duration_seconds()
        result['success_rate_percent'] = self.get_success_rate()
        result['is_running'] = self.is_running()
        result['is_completed'] = self.is_completed()
        
        if include_metrics:
            result['performance_metrics_count'] = self.performance_metrics.count()
        
        return result


class PerformanceMetrics(BaseModel):
    """
    Store various performance and analytical metrics.
    Flexible structure for tracking system and business metrics.
    """
    
    __tablename__ = "performance_metrics"
    
    # Metric identification
    metric_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Name/type of the metric being recorded"
    )
    
    metric_value = Column(
        DECIMAL(15, 4),
        nullable=True,
        comment="Numerical value of the metric"
    )
    
    metric_unit = Column(
        String(20),
        nullable=True,
        comment="Unit of measurement (seconds, percentage, count, etc.)"
    )
    
    # Temporal information
    measurement_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the metric was measured"
    )
    
    # Foreign key relationships
    stock_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Optional reference to specific stock"
    )
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Optional reference to analysis session"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional metadata and context for the metric"
    )
    
    # Relationships
    stock = relationship(
        "Stock",
        back_populates="performance_metrics",
        lazy="joined"
    )
    
    session = relationship(
        "AnalysisSession",
        back_populates="performance_metrics",
        lazy="joined"
    )
    
    # Table indexes
    __table_args__ = (
        Index("idx_performance_metrics_name_date", "metric_name", "measurement_date"),
        Index("idx_performance_metrics_stock_date", "stock_id", "measurement_date"),
        Index("idx_performance_metrics_session_name", "session_id", "metric_name"),
        Index("idx_performance_metrics_value", "metric_value"),
        
        {"comment": "Table for storing various performance and analytical metrics"}
    )
    
    @validates('metric_name')
    def validate_metric_name(self, key, metric_name):
        """Validate metric name"""
        if not metric_name or not metric_name.strip():
            raise ValueError("Metric name cannot be empty")
        return metric_name.strip()
    
    def __repr__(self) -> str:
        return (f"<PerformanceMetrics(name={self.metric_name}, value={self.metric_value}, "
                f"date={self.measurement_date})>")
    
    @classmethod
    def create_system_metric(cls, name: str, value: Decimal, unit: str = None, 
                           session_id: str = None, metadata: Dict[str, Any] = None) -> 'PerformanceMetrics':
        """
        Create a system-level performance metric.
        
        Args:
            name: Metric name (e.g., 'analysis_duration', 'memory_usage')
            value: Metric value
            unit: Unit of measurement
            session_id: Optional session reference
            metadata: Additional metadata
            
        Returns:
            PerformanceMetrics instance
        """
        return cls(
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            session_id=session_id,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_stock_metric(cls, name: str, value: Decimal, stock_id: str,
                          unit: str = None, metadata: Dict[str, Any] = None) -> 'PerformanceMetrics':
        """
        Create a stock-specific metric.
        
        Args:
            name: Metric name (e.g., 'breakout_score', 'volatility')
            value: Metric value
            stock_id: Stock reference
            unit: Unit of measurement
            metadata: Additional metadata
            
        Returns:
            PerformanceMetrics instance
        """
        return cls(
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            stock_id=stock_id,
            metadata=metadata or {}
        )
    
    def to_dict(self, include_relationships: bool = False, exclude_fields: Optional[list] = None) -> dict:
        """
        Convert performance metric to dictionary.
        
        Args:
            include_relationships: Whether to include stock/session info
            exclude_fields: List of fields to exclude
            
        Returns:
            Dictionary representation
        """
        exclude_fields = exclude_fields or []
        result = super().to_dict(exclude_fields)
        
        if include_relationships:
            if self.stock:
                result['stock'] = {
                    'symbol': self.stock.symbol,
                    'company_name': self.stock.company_name
                }
            
            if self.session:
                result['session'] = {
                    'session_name': self.session.session_name,
                    'status': self.session.status
                }
        
        return result
    
    # Common metric creation helpers
    @classmethod
    def record_analysis_duration(cls, duration_seconds: float, session_id: str = None) -> 'PerformanceMetrics':
        """Record analysis duration metric"""
        return cls.create_system_metric(
            name="analysis_duration",
            value=Decimal(str(duration_seconds)),
            unit="seconds",
            session_id=session_id
        )
    
    @classmethod
    def record_memory_usage(cls, memory_mb: float, session_id: str = None) -> 'PerformanceMetrics':
        """Record memory usage metric"""
        return cls.create_system_metric(
            name="memory_usage",
            value=Decimal(str(memory_mb)),
            unit="mb",
            session_id=session_id
        )
    
    @classmethod
    def record_breakout_confidence(cls, confidence: float, stock_id: str) -> 'PerformanceMetrics':
        """Record breakout confidence score"""
        return cls.create_stock_metric(
            name="breakout_confidence",
            value=Decimal(str(confidence)),
            stock_id=stock_id,
            unit="score"
        )
    
    @classmethod
    def record_volume_ratio(cls, ratio: float, stock_id: str) -> 'PerformanceMetrics':
        """Record volume ratio vs average"""
        return cls.create_stock_metric(
            name="volume_ratio",
            value=Decimal(str(ratio)),
            stock_id=stock_id,
            unit="ratio"
        )