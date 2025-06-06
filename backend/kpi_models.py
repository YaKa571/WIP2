from dataclasses import dataclass


@dataclass
class MerchantKPI:
    """Most Valuable Merchant KPI"""
    id: int
    mcc: int
    mcc_desc: str
    value: str


@dataclass
class VisitKPI:
    """Most Visited Merchant KPI"""
    id: int
    mcc: int
    mcc_desc: str
    visits: str


@dataclass
class UserKPI:
    """Top Spending User KPI"""
    id: int
    gender: str
    current_age: int
    value: str


@dataclass
class PeakHourKPI:
    """Peak Hour KPI"""
    hour_range: str
    value: str