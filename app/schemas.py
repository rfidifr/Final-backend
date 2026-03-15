from pydantic import BaseModel, Field,constr
from typing import Optional,Annotated
from .models import MachineStatus

# --- CARD SCHEMAS ---
class CardBase(BaseModel):
    card_id: str = Field(..., min_length=8, max_length=8)
    owner_name: str
    contact_no: str = Field(..., min_length=10, max_length=10)

class CardCreate(CardBase):
    balance: int= Field(gt=0)
    pass

class CardResponse(CardBase):
    balance: float
  

    class Config:
        from_attributes = True

# --- TRANSACTION SCHEMAS ---
class RechargeRequest(BaseModel):
    card_id: str
    amount: float = Field(..., gt=100) # Must be greater than 0

class PunchRequest(BaseModel):
    card_id: str
    machine_id: str
    
   

# --- USER & AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    arcade_id: Optional[str] = None

class RefundRequest(BaseModel):
    card_id: str
    reason: Optional[str] = "Customer request"  

class MachineCreate(BaseModel):
    id:str
    name:str
    status:MachineStatus
    cost_per_play:float
    arcade_id:str
    

class MachineResponse(BaseModel):
    id: str
    name: str
    cost_per_play: float
    arcade_id: str

class Manager_Create(BaseModel):
    username:str
    password:str
    arcade_id:str
    phone_number:Annotated[str,Field(min_length=10, max_length=15, pattern=r'^\+?\d{10,15}$')]

class Manager_Create_Response(BaseModel):
   username:str
   id:int
   arcade_id:str

class Find_Manager(BaseModel):
    username:str
    id:int
class Manager_Response(BaseModel):
    username:str
    arcade_id:str
    phone_number:str
  
    id:int
    







