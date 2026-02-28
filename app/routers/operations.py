from fastapi import APIRouter,HTTPException,Depends,status 
from sqlalchemy.orm import Session
from app import models,schemas,database
from app.dependencies import get_current_user,verify_machine

router =APIRouter(
    prefix="/ops",
    tags=['Machine operations']
)

@router.post("punch",status_code=status.HTTP_200_OK)

def punch(
    data: schemas.PunchRequest,
    machine :models.Machine=Depends(verify_machine),
    db:Session=Depends(database.get_db)

):
    card=db.query(models.Card).filter(
        models.Card.card_id== data.card_id,
        models.Card.arcade == machine.arcade_id).first()
    
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="card doesn't exist or is from another arcade")
    
    if card.balance<machine.cost_per_play:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Cost: {machine.cost_per_play}, Balance: {card.balance}"
        )
    
    card.balance -= machine.cost_per_play

    punch_log =models.PunchHistory(
        card_id=card.card_id,
        machine_id=machine.id,
        cost_at_time=machine.cost_per_play
    )

    db .add(punch_log)
    db.commit()

    return {
        "status":"success",
        "game":machine.name,
        "remaining_balance":card.balance
    }
def get_card_status(
    card_id: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    card = db.query(models.Card).filter(
        models.Card.card_id == card_id,
        models.Card.arcade_id == current_user.arcade_id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return {
        "owner": card.owner_name,
        "balance": card.balance
    }

