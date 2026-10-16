from sqlalchemy.orm import Session

from app.categories.model import Category


DEFAULT_CATEGORIES = [
    # Expense categories
    {"name": "Food", "icon": "food", "type": "expense"},
    {"name": "Shopping", "icon": "shopping", "type": "expense"},
    {"name": "Transport", "icon": "transport", "type": "expense"},
    {"name": "Housing", "icon": "home", "type": "expense"},
    {"name": "Health", "icon": "health", "type": "expense"},
    {"name": "Education", "icon": "education", "type": "expense"},
    {"name": "Bills", "icon": "bills", "type": "expense"},
    {"name": "Entertainment", "icon": "entertainment", "type": "expense"},
    {"name": "Travel", "icon": "travel", "type": "expense"},
    {"name": "Fitness", "icon": "fitness", "type": "expense"},
    {"name": "Pets", "icon": "pets", "type": "expense"},
    {"name": "Other", "icon": "shopping", "type": "expense"},

    # Income categories
    {"name": "Salary", "icon": "salary", "type": "income"},
    {"name": "Freelance", "icon": "salary", "type": "income"},
    {"name": "Investments", "icon": "investment", "type": "income"},
    {"name": "Gifts", "icon": "gift", "type": "income"},
    {"name": "Other Income", "icon": "gift", "type": "income"},
]


def create_default_categories(db: Session, user_id: int) -> None:
    categories = [
        Category(
            user_id=user_id,
            name=item["name"],
            icon=item["icon"],
            type=item["type"],
        )
        for item in DEFAULT_CATEGORIES
    ]

    db.add_all(categories)
    db.flush()