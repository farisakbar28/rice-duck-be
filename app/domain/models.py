from dataclasses import dataclass
from datetime import datetime
from typing import Any
@dataclass(frozen=True)
class RiceVariety: code:str; label:str; risk_note:str; status:str
@dataclass(frozen=True)
class PlantingSystem: code:str; label:str; recommended_density_max_are:float; recommended_density_min_are:float=2.0; note:str=""
@dataclass(frozen=True)
class DSSConstants: pass
@dataclass(frozen=True)
class ParameterMetadata: value:Any; unit:str; source:str; status:str; note:str
@dataclass(frozen=True)
class User: id:str; name:str; email:str; password_hash:str; created_at:datetime; updated_at:datetime
@dataclass(frozen=True)
class AuthContext: user:User
