from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database, security
from app.dependencies import verify_admin, get_current_user
from app.security import create_secretkey,get_password_hash
from sqlalchemy import and_,or_

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

@router.post("/create_manager", status_code=status.HTTP_201_CREATED,response_model=schemas.Manager_Create_Response) 
def create_manager(
    manager_data: schemas.Manager_Create,
    db: Session = Depends(database.get_db), 
    _ = Depends(verify_admin)
):
    arcade = db.query(models.Arcade).filter(models.Arcade.id == manager_data.arcade_id).first()
    
    if not arcade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such arcade")
    
    hashed_pwd = security.get_password_hash(manager_data.password)
    new_user = models.User(
        username=manager_data.username,
        hashed_password=hashed_pwd,
        role="manager",
        arcade_id=manager_data.arcade_id,
        phone_number=manager_data.phone_number)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
    "id": new_user.id,
    "username": new_user.username,
    "arcade_id": new_user.arcade_id,
    "message": f"Manager {new_user.username} created for arcade {new_user.arcade_id}"
}



@router.get("/manager_details", status_code=status.HTTP_200_OK, response_model=schemas.Manager_Response)
def get_manager_details(
    username: str | None = None,
    id: int | None = None,
    db: Session = Depends(database.get_db),
    current_user = Depends(verify_admin)
):
    # Base query: only managers
    query = db.query(models.User).filter(models.User.role == "manager")

    # Allow search by either username OR id
    if username and id:
        query = query.filter(or_(models.User.username == username, models.User.id == id))
    elif username:
        query = query.filter(models.User.username == username)
    elif id:
        query = query.filter(models.User.id == id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either username or id"
        )

  
    if current_user.role != "administrator":
        query = query.filter(models.User.arcade_id == current_user.arcade_id)

    user = query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or you don't have permission to view them"
        )

    return {
        "id": user.id,
        "username": user.username,
        "arcade_id": user.arcade_id,
        "phone_number": user.phone_number
    }                  

@router.get("/machine_details", status_code=status.HTTP_200_OK,response_model=schemas.machinedetailsResponse)
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

    return  {
        "id": machines.id,  
        "name": machines.name,
        "cost_per_play": machines.cost_per_play,
        "status": machines.status
    }


@router.post("/new_machine", response_model=schemas.MachineResponse)
def new_machine(
    machine_data: schemas.MachineCreate,
    secret_key: str = Depends(create_secretkey),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["manager", "administrator"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Use client-supplied arcade_id directly
    new_machine_obj = models.Machine(
        **machine_data.model_dump(),
        secret_key=secret_key
    )

    db.add(new_machine_obj)
    db.commit()
    db.refresh(new_machine_obj)

    return {
        "id": new_machine_obj.id,
        "name": new_machine_obj.name,
        "cost_per_play": new_machine_obj.cost_per_play,
        "message": "Machine created successfully"
    }