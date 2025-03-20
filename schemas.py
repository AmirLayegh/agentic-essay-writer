from typing import Annotated, List, TypedDict
from pydantic import BaseModel, Field
from datetime import datetime


class AgentState(TypedDict):
    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int
    
class Queries(BaseModel):
    queries: List[str]
    
    