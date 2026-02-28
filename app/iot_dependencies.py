import hmac
import hashlib
import time 
from fastapi import Request,HTTPException,status,Depends
from sqlalchemy.orm import Session
from app import models,database
from app.dependencies import get_current_user

ALLOWED_TIME_DRIFT =3000

async def verify_machine(
        request:Request,
        db :Session=Depends(database.get_db)
):
    machine_id=request.headers.get("X-Machine-Id")
    timestamp= request.headers.get("X-Timestamp")
    signature= request.headers.get("X-Signature")

    if not machine_id or not timestamp or not signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing authentication headers"
        )

    #  Validate timestamp format
    try:
        timestamp_int = int(timestamp)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid timestamp"
        )

    #  Prevent replay attacks
    current_time = int(time.time())
    if abs(current_time - timestamp_int) > ALLOWED_TIME_DRIFT:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request expired"
        )

    #  Fetch machine from DB 
    machine = db.query(models.Machine).filter(
        models.Machine.id == machine_id  # Changed from .id to .machine_id
        #models.Machine.arcade_id == current_user.arcade_id,
    ).first()

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid machine" 
        )

    # Get card_id from body 
    try:
        data = await request.json()  # This is already the dict, not nested
        card_id = data.get("card_id")  # Get card_id directly from data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON body: {str(e)}"
        )

    if not card_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing card_id"
        )

    #  Recreate message
    message = f"{machine_id}{card_id}{timestamp}"

    #  Recalculate HMAC
    expected_signature = hmac.new(
        machine.secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    #  comparison
    if not hmac.compare_digest(expected_signature, signature):
        print(signature)
        print(expected_signature)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    return machine