from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from app import models, schemas,database,security
from app.dependencies import verify_admin,get_current_user
from app.security import create_secretkey


router = APIRouter(prefix="/admin", tags=['admin'])

@router.post("/create-arcade",status_code=status.HTTP_201_CREATED)
def create_arcade(
    name :str ,
    location: str,
    db: Session = Depends(database.get_db),
    _ = Depends(verify_admin)
):
    arcade_id= f"ARC_{name[:3].upper()}_{location[:2].upper}"
    new_arcade=models.Arcade(id=arcade_id,name=name,location=location)
    db.add(new_arcade)
    db.commit()
    db.refresh(new_arcade)

    return {"message":"Arcade created","arcade": new_arcade}

@router.post("/create_manaager",status_code=status.HTTP_201_CREATED)
def create_manager(
    username:str,
    password:str,
    arcade_id:str,
    db: Session =Depends(database.get_db),
    _ =Depends(verify_admin)
):
    arcade= db.query(models.Arcade).filter(models.Arcade.id == arcade_id).first()
    
    if not arcade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no such arcade")
    
    hashed_pwd = security.get_password_hashed(password)
    new_user = models.User(
        username= username,
        hashed_password=hashed_pwd,
        role ="manager",
        arcade_id =arcade_id
    )
    db.add(new_user)
    db.commit()

    return {"message": f"Manager{username} created for arcade {arcade_id}"}

@router.get("/manager_details",status_code=status.HTTP_302_FOUND)
def get_manager_detials(
    queried_user:str,
    db:Session = Depends(database.get_db),
    current_user = Depends(verify_admin)
):  
    arcade_id= current_user.arcade_id
    user = (db.query(models.User).filter(
            models.User.username == queried_user,
            models.User.arcade_id == arcade_id
        ).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your arcade"
        )

    return user
@router.get("/machine_details",status_code=status.HTTP_200_OK)

def machine_details(
    name:str,
    current_user= Depends(get_current_user),
    db:Session =Depends(database.get_db)

):
    if current_user.role not in ['manager','admin','administrator']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorised access"
        )
    arcade_id=current_user.arcade_id
    machines= db.query(models.Machine).filter(models.machine.name==name,models.machine.arcade_id==arcade_id).first()

    return machines

@router.post("/new_machine", response_model=schemas.MachineResponse)
def new_machine(
    machine_data: schemas.MachineCreate,
    secret_key: str= Depends(create_secretkey),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Security: Only manager and administrator can create machines
    if current_user.role not in ["manager",'administrator']:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Create new machine linked to manage's arcade
    
    new_machine = models.Machine(
        **machine_data.model_dump(),
        arcade_id=current_user.arcade_id,secret_key=secret_key
    )

    db.add(new_machine)
    db.commit()
    db.refresh(new_machine)

    return new_machine

