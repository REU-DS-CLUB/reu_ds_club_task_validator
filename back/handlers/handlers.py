# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from back.database import SessionLocal
# from back.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
# from back.schemas.assignment import Assignment as AssignmentSchema
# from back.schemas.user import User as UserSchema
# from back.models import Task as TaskModel  
# from back.models import Assignment as AssignmentModel  
# from back.models import User as UserModel  

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/assignments/", response_model=list[AssignmentSchema])
# async def read_assignments(db: Session = Depends(get_db)):
#     try:
#         assignments = db.query(AssignmentModel).all()
#         return assignments
#     except Exception as e:
#         print(f"Error retrieving assignments: {e}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve assignments")

# @router.get("/users/", response_model=list[UserSchema])
# async def read_users(db: Session = Depends(get_db)):
#     try:
#         users = db.query(UserModel).all()
#         return users
#     except Exception as e:
#         print(f"Error retrieving users: {e}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve users")

# @router.get("/tasks/", response_model=list[TaskSchema])
# async def read_tasks(db: Session = Depends(get_db)):
#     try:
#         tasks = db.query(TaskModel).all()
#         return tasks
#     except Exception as e:
#         print(f"Error retrieving tasks: {e}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve tasks")

# @router.post("/tasks/", response_model=TaskSchema)
# async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
#     try:
#         db_task = TaskModel(
#             task_name=task.task_name,
#             task_status=task.task_status,
#             task_description=task.task_description,
#             task_type=task.task_type,
#             task_data=task.task_data,
#             requirements=task.requirements
#         )
#         db.add(db_task)
#         db.commit()
#         db.refresh(db_task)
#         return db_task
#     except Exception as e:
#         print(f"Error creating task: {e}")
#         raise HTTPException(status_code=500, detail="Failed to create task")

# @router.put("/tasks/{task_id}", response_model=TaskSchema)
# async def edit_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
#     db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
#     if not db_task:
#         raise HTTPException(status_code=404, detail="Task not found")

#     try:
#         db_task.task_name = task.task_name or db_task.task_name
#         db_task.task_status = task.task_status or db_task.task_status
#         db_task.task_description = task.task_description or db_task.task_description
#         db_task.task_type = task.task_type or db_task.task_type
#         db_task.task_data = task.task_data or db_task.task_data
#         db_task.requirements = task.requirements or db_task.requirements

#         db.commit()
#         db.refresh(db_task)
#         return db_task
#     except Exception as e:
#         print(f"Error updating task: {e}")
#         raise HTTPException(status_code=500, detail="Failed to update task")
