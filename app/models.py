from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Boolean, Integer,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


import enum

class MachineStatus(str, enum.Enum):
    online = "ACTIVE"
    offline = "INACTIVE"
    busy = "BLOCKED"
    a= "EXPIRED"
class cardStatus(str,enum.Enum):
    active="Active"
    passive="Depreciated"

class mem_status(str,enum.Enum):
    vip="VIP"
    ord="ORD"

class Arcade(Base):
    __tablename__ = "arcades"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)

    users = relationship("User", back_populates="arcade")
    machines = relationship("Machine", back_populates="arcade")
    cards = relationship("Card", back_populates="arcade")

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="manager") # 'administrator' or 'manager'
    arcade_id = Column(String, ForeignKey("arcades.id"), nullable=True)
    phone_number = Column(String, nullable=True)
    sms_opt_in = Column(Boolean, default=True)
    #membership =Column(Enum(mem_status),nullable=False, default="ord")
    arcade = relationship("Arcade", back_populates="users")

class Machine(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost_per_play = Column(Float, default=1.0)
    arcade_id = Column(String, ForeignKey("arcades.id"))
    secret_key = Column(String,nullable=False)
    #status=Column(Enum(MachineStatus),nullable=False,default="online")

    arcade = relationship("Arcade", back_populates="machines")

class Card(Base):
    __tablename__ = "cards"
    card_id = Column(String, primary_key=True, index=True)
    owner_name = Column(String)
    contact_no = Column(String(10))
    balance = Column(Float, default=0.0)
    arcade_id = Column(String, ForeignKey("arcades.id"))
    #status=Column(Enum(cardStatus),nullable=False,default="active")
    issue_data=Column(DateTime,nullable=False)
    expiry_data=Column(DateTime,nullable=False)
    
    arcade = relationship("Arcade", back_populates="cards")

class RechargeHistory(Base):
    __tablename__ = "recharge_history"
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(String, ForeignKey("cards.card_id"))
    amount = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    payment_type=Column(String,nullable=False,default="Cash")

class PunchHistory(Base):
    __tablename__ = "punch_history"
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(String, ForeignKey("cards.card_id"))
    machine_id = Column(String, ForeignKey("machines.id"))
    arcade_id = Column(String, ForeignKey("arcades.id"))
    cost_at_time = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# class Promotion(Base):
#     __tablename__ = "promotions"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     arcade_id = Column(String, ForeignKey("arcades.id"))
#     title = Column(String, nullable=False)
#     message = Column(Text, nullable=False)
#     is_sent = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

# class SMSLog(Base):
#     __tablename__ = "sms_logs"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     promotion_id = Column(UUID)
#     user_id = Column(String)
#     phone_number = Column(String)
#     twilio_sid = Column(String)
#     status = Column(String, default="sent")
#     created_at = Column(DateTime, default=datetime.utcnow)