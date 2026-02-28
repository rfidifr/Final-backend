from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app import models,schemas,database
from app.dependencies import get_current_user
from app.security import create_secretkey

router =APIRouter(
    prefix="/manager",
    tags=["manager operations"]
)

@router.post("/create_card",status_code=status.HTTP_201_CREATED)
def create_card(
    card_data: schemas.CardCreate,
    db:Session = Depends(database.get_db),
    current_user : models.User = Depends(get_current_user)
):
    if current_user.role not in ['manager','admin','administrator']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,details="permission denied")
    
    new_card = models.card(
        **card_data.model_dump,
        arcade_id=current_user.arcade_id
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    return new_card

@router.put("/recharge")

def recharge(
    data:schemas.RechargeRequest,
    current_user: models.User=Depends(get_current_user),
    db:Session=Depends(database.get_db)

):
    card=db.query(models.card).filter(
        models.card.card_id==data.card_id,
        models.card.arcade_id==data.arcade_id
    ).first()

    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="card not found")
    
    card.balance+=data.amount

    log=models.RechargeHistory(card_id=card.card_id,amount=data.amount)
    db.add(log)
    db.commit()
    return {"message":"recharge successful","new balance":card.balance}

@router.put("/refund")

def refund(
    data:schemas.RefundRequest,
    db:Session = Depends(database.get_db),
    current_user : models.User=Depends(get_current_user),

):
    card=db.query(models.Card).filter(
        models.Card.card_id==data.card_id,
        models.Card.arcade_id==current_user.arcade_id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="card doesn't exist or not linked to this arcade"

        )
    refund_amount=card.balance

    card.balance=0

    refund_log=models.RechargeHistory(
        card_id=card.card_id,
        amount=-refund_amount
    )
    db.add(refund_log)
    db.commit()

    return {
        "message": "Refund processed successfully",
        "card_id": card.card_id,
        "refunded_amount": refund_amount,
        "new_balance": 0.0
    }

@router.get("/punch_history",status_code=status.HTTP_200_OK)
def punch_history(
    current_user:models.User=Depends(get_current_user),
    db:Session = Depends(database.get_db)
):
    if current_user.role not in ['manager','admin','administrator']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "unautherized access"
        )
    hist=db.query(models.PunchHistory).filter(models.PunchHistory.arcade_id== current_user.arcade_id).all()

    return hist
