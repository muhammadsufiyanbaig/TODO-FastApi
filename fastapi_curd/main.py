from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(index=True)
   


sqlite_url = f"postgresql://neondb_owner:iWK6s9ImyHgV@ep-steep-art-a5nfu9wr.us-east-2.aws.neon.tech/neondb?sslmode=require"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    yield
 
app = FastAPI(lifespan=lifespan)

@app.post("/task/")
def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    
@app.put("/task/")
def update_task(task: Task):
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task.id)
        results = session.exec(statement)
        db_task = results.one()
        db_task.content = task.content
        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        return db_task
    
    

@app.get("/task/")
def read_task():
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()
        return tasks
    
@app.delete("/task/")
def delete_task(task:Task):
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task.id)
        results = session.exec(statement)
        db_task = results.one()
        print("Task: ", db_task)
        session.delete(db_task)
        session.commit()
        return "Task deleted ......"
