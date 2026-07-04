from fastapi import FastAPI, HTTPException ,status, Response
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
#------Custom Modules
from pydantic_schemas import *


# Initializing the main TaskFlow application
app = FastAPI(title="TaskFlow API")



# ==========================================
# 💾 IN-MEMORY DATABASE SETUP
# ==========================================
from datetime import date

MOCK_TASKS = [
    {
        "id": 1, 
        "title": "Configure production database", 
        "description": "Set up PostgreSQL instances with automated daily backups.",
        "done": True, 
        "priority": "high", 
        "is_urgent": True, 
        "due_date": date(2026, 8, 2),
        "task_status": "done"
    },
    {
        "id": 2, 
        "title": "Design TaskFlow login screen", 
        "description": None,
        "done": False, 
        "priority": "medium", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 4),
        "task_status": "todo"
    },
    {
        "id": 3, 
        "title": "Write Lesson 1.4 backend code", 
        "description": "Implement the CRUD endpoints for the new tasks resource.",
        "done": False, 
        "priority": "low", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 5),
        "task_status": "inprogress"
    },
    {
        "id": 4, 
        "title": "Update API documentation", 
        "description": "Ensure Swagger UI reflects the new is_urgent and due_date fields.",
        "done": False, 
        "priority": "medium", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 7),
        "task_status": "todo"
    },
    {
        "id": 5, 
        "title": "Patch critical security vulnerability", 
        "description": "Update dependencies to fix the reported zero-day exploit.",
        "done": False, 
        "priority": "high", 
        "is_urgent": True, 
        "due_date": date(2026, 8, 1),
        "task_status": "inprogress"
    },
    {
        "id": 6, 
        "title": "Refactor Pydantic schemas", 
        "description": None,
        "done": True, 
        "priority": "medium", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 10),
        "task_status": "done"
    },
    {
        "id": 7, 
        "title": "Migrate user data to new servers", 
        "description": "Move all user profile images to the new AWS S3 bucket.",
        "done": False, 
        "priority": "high", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 15),
        "task_status": "todo"
    },
    {
        "id": 8, 
        "title": "Draft monthly team newsletter", 
        "description": None,
        "done": False, 
        "priority": "low", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 28),
        "task_status": "todo"
    },
    {
        "id": 9, 
        "title": "Fix pagination bug on dashboard", 
        "description": "Users are reporting that clicking page 2 throws a 500 error.",
        "done": False, 
        "priority": "high", 
        "is_urgent": True, 
        "due_date": date(2026, 8, 3),
        "task_status": "inprogress"
    },
    {
        "id": 10, 
        "title": "Conduct code review for PR #42", 
        "description": None,
        "done": True, 
        "priority": "low", 
        "is_urgent": False, 
        "due_date": date(2026, 8, 12),
        "task_status": "done"
    }
]

#fixed & strict choices for priority
class Priorityenum(str, Enum):
    HIGH="high"
    MEDIUM="medium"
    LOW="low"

#fixed & strict Status of task
class Statusenum(str, Enum):
    TODO="todo",
    INPROGRESS="inprogress",
    DONE="done"


# ==========================================
# UTILITY - START
# ==========================================


def check_duplicate_title(title: str, task_list: list) -> bool :
    for task in task_list:
        if title == task["title"]:
            return False    
    return True


# ==========================================
# UTILITY - END
# ==========================================


# ==========================================
# 🛠️ CRUD ENDPOINTS - START
# ==========================================


# The Root Entrance Endpoint

@app.get("/")
async def read_root():
    return {
        "project": "TaskFlow API",
        "version": "1.0.0",
        "status": "Online"
    }



# CREATE (POST) - 201 CREATED
@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskRead)
async def create_task(task_in: TaskCreate):

    if not check_duplicate_title(task_in.title, MOCK_TASKS):
        return Response(status_code=status.HTTP_409_CONFLICT)

    new_id = MOCK_TASKS[-1]["id"] + 1 if MOCK_TASKS else 1

    # Merge Validated Client Input Data with System Data

    new_task={
        "id": new_id,
        "title": task_in.title,
        "description": task_in.description,
        "done": False,
        "priority": task_in.priority,
        "task_status": "todo",
        "is_urgent": task_in.is_urgent,
        "due_date": task_in.due_date
    }
    MOCK_TASKS.append(new_task)
    return new_task





# Get a list of tasks and allows filltereing based on task completetion and priority 


# GET ALL COMPLETED TAST - 200 OK - TESTED
@app.get("/tasks/completed", status_code=status.HTTP_200_OK)
async def get_completed_task():
    completed_task=[ct for ct in MOCK_TASKS if ct["done"]==True]
    return completed_task

# Query Params and GET ALL (GET) - 200 OK - TESTED
@app.get("/tasks", status_code=status.HTTP_200_OK, response_model=list[TaskRead])
async def get_tasks(
    done : bool | None=None,
    priority : Priorityenum | None=None,
    task_status: Statusenum | None=None,
    limit : int=10,
    search: str | None=None,
    is_urgent : bool | None=None

    ):

    filtered_tasks = MOCK_TASKS

    if done is not None:
        filtered_tasks = [f for f in filtered_tasks if f["done"]==done]

    if priority is not None:
        filtered_tasks = [f for f in filtered_tasks if f["priority"]==priority.value]

    if task_status is not None:
        filtered_tasks = [f for f in filtered_tasks if f["task_status"]==task_status.value]

    if search is not None:
        filtered_tasks =[f for f in filtered_tasks if search.lower() in f["title"].lower()]

    if is_urgent is not None:
        filtered_tasks = [f for f in filtered_tasks if f["is_urgent"]==is_urgent]  
    
    return filtered_tasks


# 3. The Tasks Resource Endpoint (Hardcoded for now) - TESTED
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def get_task_by_id(task_id: int):
    for task in MOCK_TASKS:
        if task["id"]==task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with {task_id} doen't exist"
    )    


#UPDATE (PATCH) - 200 OK
@app.patch("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
async def update_task(task_id: int, task_in: TaskUpdate):
    for task in MOCK_TASKS:
        if task["id"] == task_id:
            if task_in.title is not None:
                if not check_duplicate_title(task_in.title, MOCK_TASKS):
                    return Response(status_code=status.HTTP_409_CONFLICT)
                task["title"] = task_in.title
            if task_in.done is not None:
                task["done"] = task_in.done
            if task_in.priority is not None:
                task["priority"] = task_in.priority
            if task_in.task_status is not None:
                task["task_status"] = task_in.task_status
            if task_in.is_urgent is not None:
                task["is_urgent"] = task_in.is_urgent
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found")

# DELETE (DELETE) - 204 No Content            
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, )
async def delete_task(task_id: int):
    for index, task in enumerate(MOCK_TASKS):
        if task["id"] == task_id:
            MOCK_TASKS.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Not Found")


# ==========================================
# 🛠️ CRUD ENDPOINTS - START
# ==========================================














@app.get("/project/info", status_code=status.HTTP_200_OK)
async def get_project_info():
    return {"team_size":5}


@app.get("/health")
async def get_health_status():
    return {"status": "healthy"}