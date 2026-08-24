"""Frozen Model C formulas; research candidates never enter production."""
from datetime import date, timedelta
from decimal import Decimal
Y0_C=Decimal("50.0"); P_GABAH=Decimal("6000"); P_BUY=Decimal("25000"); P_SELL=Decimal("45000")
def compute_age_status(age:int): return "NOT_RECOMMENDED" if age<21 else "LOCAL_READY" if age<=30 else "OLDER_CONSERVATIVE"
def compute_density(duck_count:int, area:Decimal, system:str):
    d=Decimal(duck_count)/area
    status="HIGH_RISK" if d>8 else "UNDER" if d<2 else "RECOMMENDED" if d <= (Decimal(4) if system=="jajar_legowo" else Decimal(3)) else "WARNING_ABOVE_RECOMMENDED"
    return d,d*100,status
def compute_calendar(anchor:date|None): return (None,None,None,None) if anchor is None else tuple(anchor+timedelta(days=x) for x in (21,30,56,60))
def compute_yield(area:Decimal): return Y0_C,Y0_C*area
def compute_economics(*,total:Decimal,ducks:int,density:Decimal,p_gabah:Decimal,p_buy:Decimal,p_sell:Decimal,feed:Decimal|None,jaring:Decimal|None,nj:Decimal|None,kandang:Decimal|None,nk:Decimal|None):
    rice=total*p_gabah; buy=Decimal(ducks)*p_buy; duck=None if density>8 else Decimal(ducks)*p_sell; before=None if duck is None else rice+duck-buy
    infra=(jaring/nj if jaring is not None else Decimal(0))+(kandang/nk if kandang is not None else Decimal(0)) if jaring is not None or kandang is not None else None
    after=None if before is None or (feed is None and infra is None) else before-(feed or Decimal(0))-(infra or Decimal(0))
    return rice,duck,buy,feed,infra,before,after
