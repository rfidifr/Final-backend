from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, security, database

router = APIRouter(tags=["login"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@router.post("/token", tags=["Authentication"])
def login_for_access_token(
    db: Session = Depends(database.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # 1. Fetch user
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # 2. Verify existence and password
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. ENFORCE ROLE LOGIC: Managers must have an arcade; Admins do not.
    if user.role == "manager" and not user.arcade_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager account is not assigned to an arcade. Contact Admin."
        )

    # 4. Generate JWT with identity and role metadata
    access_token = security.create_access_token(
        data={
            "sub": user.username, 
            "role": user.role, 
            "arcade_id": user.arcade_id
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}