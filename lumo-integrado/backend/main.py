from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Task, User
from security import hash_password, verify_password

SECRET_KEY = "lumo-secret-key-2024"
ALGORITHM = "HS256"
TOKEN_HOURS = 8

app = FastAPI(title="Lumo API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: Optional[str] = ""
    category: str = "work"
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[str] = None
    done: bool = False


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    due_date: Optional[str]
    done: bool
    created_at: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_sample_tasks(db: Session, user_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    samples = [
        Task(
            title="Organizar primeiras tarefas",
            description="Monte o seu quadro inicial no Lumo.",
            category="work",
            priority="medium",
            status="todo",
            due_date=today,
            done=False,
            created_at=datetime.now().isoformat(),
            user_id=user_id,
        ),
        Task(
            title="Personalizar rotina de estudos",
            description="Separe uma tarefa para prática e outra para revisão.",
            category="study",
            priority="medium",
            status="doing",
            due_date=today,
            done=False,
            created_at=datetime.now().isoformat(),
            user_id=user_id,
        ),
        Task(
            title="Concluir cadastro",
            description="Sua conta já está pronta para uso.",
            category="personal",
            priority="low",
            status="done",
            due_date=today,
            done=True,
            created_at=datetime.now().isoformat(),
            user_id=user_id,
        ),
    ]
    db.add_all(samples)
    db.commit()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_error
    return user


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Lumo API rodando! Acesse /docs para ver os endpoints."}


@app.post("/api/auth/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    create_sample_tasks(db, user.id)

    return {
        "access_token": create_token(user.email),
        "token_type": "bearer",
        "user_name": user.name,
        "user_email": user.email,
    }


@app.post("/api/auth/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form.username.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    return {
        "access_token": create_token(user.email),
        "token_type": "bearer",
        "user_name": user.name,
        "user_email": user.email,
    }


@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Task)
        .filter(Task.user_id == user.id)
        .order_by(Task.id.asc())
        .all()
    )


@app.post("/api/tasks", response_model=TaskOut, status_code=201)
def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = Task(
        **data.model_dump(),
        created_at=datetime.now().isoformat(),
        user_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    for field, value in data.model_dump().items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    db.delete(task)
    db.commit()
