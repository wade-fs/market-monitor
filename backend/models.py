from dataclasses import dataclass, field, asdict
from typing import Optional, List

@dataclass
class SeriesPoint:
    t: str
    v: float

@dataclass
class Indicator:
    id: str; country: str; category: str; name: str; unit: str; frequency: str
    current: Optional[float]; previous: Optional[float]; change: Optional[float]
    trend: str; updated_at: str
    series: List[SeriesPoint] = field(default_factory=list)
    source: str = ""; error: Optional[str] = None
    def to_dict(self):
        d = asdict(self); d["series"] = [{"t":p.t,"v":p.v} for p in self.series]; return d

@dataclass
class StockQuote:
    ticker: str; name: str; country: str
    price: Optional[float]; change: Optional[float]; pct: Optional[float]
    volume: Optional[float]; market_cap: Optional[float]; updated_at: str
    error: Optional[str] = None
    def to_dict(self): return asdict(self)

@dataclass
class Fundamentals:
    ticker: str; name: str; country: str; period: str
    revenue: Optional[float] = None; gross_profit: Optional[float] = None
    operating_income: Optional[float] = None; net_income: Optional[float] = None
    eps: Optional[float] = None; revenue_yoy: Optional[float] = None
    eps_yoy: Optional[float] = None; gross_margin: Optional[float] = None
    op_margin: Optional[float] = None; net_margin: Optional[float] = None
    total_assets: Optional[float] = None; total_liabilities: Optional[float] = None
    equity: Optional[float] = None; cfo: Optional[float] = None
    capex: Optional[float] = None; fcf: Optional[float] = None
    source: str = ""; error: Optional[str] = None
    def to_dict(self): return asdict(self)

@dataclass
class Valuation:
    ticker: str; name: str; country: str; date: str
    pe: Optional[float] = None; pb: Optional[float] = None
    ps: Optional[float] = None; ev_ebitda: Optional[float] = None
    dividend_yield: Optional[float] = None; peg: Optional[float] = None
    roe: Optional[float] = None; roa: Optional[float] = None
    debt_equity: Optional[float] = None
    source: str = ""; error: Optional[str] = None
    def to_dict(self): return asdict(self)

@dataclass
class CompanySnapshot:
    ticker: str; name: str; country: str; sector: str
    quote: Optional[dict] = None
    fundamentals: List[dict] = field(default_factory=list)
    valuation: Optional[dict] = None; updated_at: str = ""
    def to_dict(self): return asdict(self)
