from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session 
from app import models, schemas, database, security
from app.dependencies import verify_admin, get_current_user
from app.security import create_secretkey

router = APIRouter(prefix="/admin", tags=['admin'])

@router.post("/create-arcade", status_code=status.HTTP_201_CREATED)
def create_arcade(
    name: str, 
    location: str, 
    db: Session = Depends(database.get_db), 
    _ = Depends(verify_admin)
):
    # Fixed: Added () to .upper()
    arcade_id = f"ARC_{name[:3].upper()}_{location[:2].upper()}"
    
    new_arcade = models.Arcade(id=arcade_id, name=name, location=location)
    db.add(new_arcade)
    db.commit()
    db.refresh(new_arcade)

    return {"message": "Arcade created", "arcade": new_arcade}

@router.post("/create_manager", status_code=status.HTTP_201_CREATED) # Fixed typo in function name
def create_manager(
    username: str, 
    password: str, 
    arcade_id: str, 
    db: Session = Depends(database.get_db), 
    _ = Depends(verify_admin)
):
    arcade = db.query(models.Arcade).filter(models.Arcade.id == arcade_id).first()
    
    if not arcade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such arcade")
    
    hashed_pwd = security.get_password_hashed(password)
    new_user = models.User(
        username=username,
        hashed_password=hashed_pwd,
        role="manager",
        arcade_id=arcade_id
    )
    db.add(new_user)
    db.commit()

    return {"message": f"Manager {username} created for arcade {arcade_id}"}

@router.get("/manager_details", status_code=status.HTTP_200_OK) # Changed 302 to 200 (Success)
def get_manager_details(
    queried_user: str, 
    db: Session = Depends(database.get_db), 
    current_user = Depends(verify_admin)
):  
    
    query = db.query(models.User).filter(models.User.username == queried_user)
    
    if current_user.role != "administrator":
        query = query.filter(models.User.arcade_id == current_user.arcade_id)

    user = query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or you don't have permission to view them"
        )

    return user

@router.get("/machine_details", status_code=status.HTTP_200_OK)
def machine_details(
    name: str, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(database.get_db)
):
    if current_user.role not in ['manager', 'admin', 'administrator']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized access"
        )
    
    machines = db.query(models.Machine).filter(
        models.Machine.name == name, 
        models.Machine.arcade_id == current_user.arcade_id
    ).first()

    if not machines:
        raise HTTPException(status_code=404, detail="Machine not found in your arcade")

    return machines

@router.post("/new_machine", response_model=schemas.MachineResponse)
def new_machine(
    machine_data: schemas.MachineCreate, 
    secret_key: str = Depends(create_secretkey), 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["manager", "administrator"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Fixed: secret_key assignment
    new_machine_obj = models.Machine(
        **machine_data.model_dump(),
        arcade_id=current_user.arcade_id,
        secret_key=secret_key
    )

    db.add(new_machine_obj)
    db.commit()
    db.refresh(new_machine_obj)

    return new_machine_obj

