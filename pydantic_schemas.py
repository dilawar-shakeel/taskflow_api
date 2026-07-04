from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


#---------------------| Start of OUTBOUND / INBOUND Schemas |---------------------

#Inbound Schema: What we require when creating a Task
class TaskCreate(BaseModel):
    title: str = Field(min_length=3,max_length=100)
    description: str | None = Field(default=None, max_length=500)
    priority: str = Field(default="low", min_length=3, max_length=6)
    task_status: str = Field(default="todo", min_length=4, max_length=10)
    is_urgent: bool = Field(default=False)
    due_date: date

    @field_validator("due_date")
    @classmethod
    def check_due_date_is_not_is_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Date Cannot be in the past")
        return value
    
    @field_validator("title")
    @classmethod
    def check_if_title_is_only_space(cls, title: str) -> str:
        if not title.strip():
            raise ValueError("A title cannot consist on blank spces only") 
        return title
        
    
    @model_validator(mode="after")
    def check_urgent_tast_must_have_description(self) -> "TaskCreate":
        if self.is_urgent and self.description is None:
            raise ValueError("Urgent task must add a descriptive note explaining why")
        return self
    
    @model_validator(mode="after")
    def emergency_word_in_title(self) -> "TaskCreate":
        if "emergency" in self.title.lower() and not self.is_urgent:
            raise ValueError("Tasks marked as an Emergency must have the 'is_urgent' flag set to True.")
        return self        

#Inbound Schema: What we allow when UPDATING a Task(Partial Modificaiton)
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3,max_length=100)
    done: bool | None = Field(default=None)
    priority: str | None = Field(default=None)
    is_urgent: bool | None = Field(default=None)
    task_status: str | None = Field(default=None)

#Outbound Schema: what the user will Read
class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    done: bool
    priority: str
    task_status: str
    is_urgent: bool
    due_date: date

#---------------------| End of OUTBOUND / INBOUND Schemas |--------------------- 

class Assignee(BaseModel):
    name: str
    email: EmailStr # to ensure string matches actual email rules.

class Tag(BaseModel):
    name: str = Field(min_length=2, description=" The name of the tag")
    color: str = Field(default="#FFFFFF")

class Task(BaseModel):
    title: str = Field(
        min_length=3, 
        max_length=100, 
        description="A concise title for the Team Task.")
    
    despcription: str | None =Field(
        default=None, 
        max_length=500, 
        description="Detailed notes explaining the task requirements.")
    
    done: bool = Field(
        default=False, 
        description="Tracks if the task is completed.")
    
    priority_score: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Priority ranking from 1 (lowest) to 5 (highest)."
    )

    estimate_hours: float =Field(
        default=1.0, 
        ge=0, 
        description="Estimated time to complete the task")

    tages: list[Tag]= Field(default=[])
    
    assignee: Assignee | None = Field(
        default=None,
        description="The team member assigned to this task."
    )

# good_data = {
#     "title": "Fix login bug",
#     "priority_score": 5,
#     "assignee": {"name": "Alice", "email": "alice@taskflow.com"}
# }

# bad_data = {
#     "title": "Go", 
#     "priority_score": 10,
#     "assignee": {"name": "Bob", "email": "not-an-email"}
# }

# taskinstance = Task(**bad_data)
# print(taskinstance)