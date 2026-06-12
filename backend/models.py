# models.py — 統一資料格式（對應 MACRO_PLATFORM_V4.md 規格）

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime


@dataclass
class SeriesPoint:
    t: str    # ISO date string "2026-01-01"
    v: float  # value


@dataclass
class Indicator:
    id:         str
    country:    str
    category:   str          # Growth / Inflation / Liquidity / Rates / Labor / Trade / FX / Market
    name:       str
    unit:       str
    frequency:  str          # daily / monthly / quarterly
    current:    Optional[float]
    previous:   Optional[float]
    change:     Optional[float]
    trend:      str          # up / down / flat / unknown
    updated_at: str
    series:     List[SeriesPoint] = field(default_factory=list)
    source:     str = ""     # fred / finmind / yfinance
    error:      Optional[str] = None

    def to_dict(self):
        d = asdict(self)
        d["series"] = [{"t": p.t, "v": p.v} for p in self.series]
        return d


@dataclass
class HeatmapCell:
    country:   str
    indicator: str
    value:     Optional[float]
    signal:    int           # 1=positive 0=neutral -1=negative
    label:     str


@dataclass
class CountryDashboard:
    country:    str
    updated_at: str
    growth:     List[dict] = field(default_factory=list)
    inflation:  List[dict] = field(default_factory=list)
    liquidity:  List[dict] = field(default_factory=list)
    rates:      List[dict] = field(default_factory=list)
    labor:      List[dict] = field(default_factory=list)
    trade:      List[dict] = field(default_factory=list)
    fx:         List[dict] = field(default_factory=list)
    markets:    List[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class GlobalOverview:
    risk_score:   float
    risk_label:   str         # Low / Moderate / Elevated / High
    updated_at:   str
    kpis:         List[dict] = field(default_factory=list)   # 精選重要指標
    heatmap:      dict        = field(default_factory=dict)
    markets:      List[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
