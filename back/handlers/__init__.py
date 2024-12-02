from fastapi import APIRouter
from .user_handlers import router as user_router
from .task_handlers import router as task_router
from .assignment_handlers import router as assignment_router

router = APIRouter()
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(task_router, prefix="/tasks", tags=["tasks"])
router.include_router(assignment_router, prefix="/assignments", tags=["assignments"])