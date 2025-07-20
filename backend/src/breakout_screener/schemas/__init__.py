"""
Pydantic schemas for API request/response validation and serialization
"""

from .analysis import (
    AnalysisSessionBase,
    AnalysisSessionCreate,
    AnalysisSessionFilter,
    AnalysisSessionList,
    AnalysisSessionResponse,
    AnalysisSessionSummary,
    AnalysisSessionUpdate,
    PerformanceMetricsBase,
    PerformanceMetricsCreate,
    PerformanceMetricsFilter,
    PerformanceMetricsList,
    PerformanceMetricsResponse,
    PerformanceMetricsSummary,
    PerformanceMetricsUpdate,
)
from .base import BaseSchema, PaginationParams, SortParams, TimestampMixin, UUIDMixin
from .breakout_data import (
    BreakoutDataBase,
    BreakoutDataCreate,
    BreakoutDataFilter,
    BreakoutDataList,
    BreakoutDataResponse,
    BreakoutDataSummary,
    BreakoutDataUpdate,
    DailyBreakoutSummary,
)
from .master_data import (
    MasterBreakoutDataBase,
    MasterBreakoutDataCreate,
    MasterBreakoutDataFilter,
    MasterBreakoutDataList,
    MasterBreakoutDataResponse,
    MasterBreakoutDataSummary,
    MasterBreakoutDataUpdate,
)
from .stock import (
    StockBase,
    StockCreate,
    StockFilter,
    StockList,
    StockResponse,
    StockSearch,
    StockSummary,
    StockUpdate,
)

__all__ = [
    # Base schemas
    "BaseSchema", "TimestampMixin", "UUIDMixin", "PaginationParams", "SortParams",

    # Stock schemas
    "StockBase", "StockCreate", "StockUpdate", "StockResponse", "StockList",
    "StockSearch", "StockFilter", "StockSummary",

    # BreakoutData schemas
    "BreakoutDataBase", "BreakoutDataCreate", "BreakoutDataUpdate",
    "BreakoutDataResponse", "BreakoutDataList", "BreakoutDataFilter",
    "BreakoutDataSummary", "DailyBreakoutSummary",

    # MasterBreakoutData schemas
    "MasterBreakoutDataBase", "MasterBreakoutDataCreate", "MasterBreakoutDataUpdate",
    "MasterBreakoutDataResponse", "MasterBreakoutDataList", "MasterBreakoutDataFilter",
    "MasterBreakoutDataSummary",

    # Analysis schemas
    "AnalysisSessionBase", "AnalysisSessionCreate", "AnalysisSessionUpdate",
    "AnalysisSessionResponse", "AnalysisSessionList", "AnalysisSessionFilter",
    "AnalysisSessionSummary", "PerformanceMetricsBase", "PerformanceMetricsCreate",
    "PerformanceMetricsUpdate", "PerformanceMetricsResponse", "PerformanceMetricsList",
    "PerformanceMetricsFilter", "PerformanceMetricsSummary",
]
