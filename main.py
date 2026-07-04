from fastapi import FastAPI, HTTPException ,status
from enum import Enum

# Initializing the main TaskFlow application
app = FastAPI(title="TaskFlow API")

# Our placeholder database list
MOCK_TASKS = [
    {"id": 1, "title": "Configure production database", "done": True, "priority": "high"},
    {"id": 2, "title": "Design TaskFlow login screen", "done": False, "priority": "medium"},
    {"id": 3, "title": "Write Lesson 1.4 backend code", "done": False, "priority": "low"}
]

#fixed & strict choices for priority
class Priorityenum(str, Enum):
    HIGH="high"
    MEDIUM="medium"
    LOW="low"


# The Root Entrance Endpoint
@app.get("/")
async def read_root():
    return {
        "project": "TaskFlow API",
        "version": "1.0.0",
        "status": "Online"
    }

@app.get("/tasks", status_code=status.HTTP_200_OK)
async def get_task(
    done : bool | None=None,
    priority : Priorityenum | None=None,
    limit : int=10,
    search: str | None=None
    ):

    filtered_tasks = MOCK_TASKS

    if done is not None:
        filtered_tasks = [f for f in filtered_tasks if f["done"]==done]

    if priority is not None:
        filtered_tasks = [f for f in filtered_tasks if f["priority"]==priority]

    if search is not None:
        filtered_tasks =[f for f in filtered_tasks if search.lower() in f["title"].lower()]
    
    return filtered_tasks[:limit]


@app.get("/tasks/completed", status_code=status.HTTP_200_OK)
async def get_completed_task():
    completed_task=[ct for ct in MOCK_TASKS if ct["done"]==True]
    return completed_task


# 3. The Tasks Resource Endpoint (Hardcoded for now)
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def get_tasks(task_id: int):
    for task in MOCK_TASKS:
        if task["id"]==task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with {task_id} doen't exist"
    )    


@app.get("/project/info", status_code=status.HTTP_200_OK)
async def get_project_info():
    return {"team_size":5}

@app.get("/health")
async def get_health_status():
    return {"status": "healthy"}