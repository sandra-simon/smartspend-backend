
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.transactions.router import router as transactions_router
from app.categories.router import router as categories_router
from app.budgets.router import router as budgets_router
from app.dashboard.router import router as dashboard_router
from app.analytics.router import router as analytics_router


app = FastAPI(
    title="SmartSpend API",
    description="Backend API for SmartSpend",
    version="1.0.0",
)

# Allow the local React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(budgets_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "SmartSpend API is running",
    }
