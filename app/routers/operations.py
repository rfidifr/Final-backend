from fastapi import APIRouter, HTTPException, Depends, status 
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.dependencies import get_current_user
from app.iot_dependencies import verify_machine

router = APIRouter(
    prefix="/ops",
    tags=['Machine operations']
)

@router.post("/punch", status_code=status.HTTP_200_OK)
def punch(
    data: schemas.PunchRequest,
    machine: models.Machine = Depends(verify_machine),
    db: Session = Depends(database.get_db)
):
    # Search for the card and ensure it belongs to the SAME arcade as the machine
    card = db.query(models.Card).filter(
        models.Card.card_id == data.card_id,
        models.Card.arcade_id == machine.arcade_id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card doesn't exist or belongs to a different arcade branch"
        )
    
    # Check if the card has enough funds
    if card.balance < machine.cost_per_play:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Cost: {machine.cost_per_play}, Balance: {card.balance}"
        )
    
    # Deduct balance
    card.balance -= machine.cost_per_play

    # Log the transaction
    punch_log = models.PunchHistory(
        card_id=card.card_id,
        machine_id=machine.id,
        arcade_id=machine.arcade_id, # Added to track which branch the punch happened at
        cost_at_time=machine.cost_per_play
    )

    db.add(punch_log)
    db.commit()
    db.refresh(card)

    return {
        "status": "success",
        "game": machine.name,
        "remaining_balance": card.balance
    }

@router.get("/card-status/{card_id}")
def get_card_status(
    card_id: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Ensures managers can only check cards belonging to their specific arcade
    card = db.query(models.Card).filter(
        models.Card.card_id == card_id,
        models.Card.arcade_id == current_user.arcade_id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found in your arcade")

    return {
        "card_id": card.card_id,
        "owner": card.owner_name,
        "balance": card.balance,
        "contact": card.contact_no
    }