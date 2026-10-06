# SmartSpend

SmartSpend is a personal finance management application for tracking income and expenses, managing categories and monthly budgets, and analyzing spending through dashboards and analytics.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Argon2
- Docker & Docker Compose
- GitHub Actions

## Features

- User registration and authentication
- JWT access and refresh tokens
- Password reset via email
- Income and expense tracking
- Transaction search, filtering, sorting, and pagination
- Custom income and expense categories
- Optional monthly budgets
- Dashboard with financial summaries and expense breakdown
- Financial analytics and spending trends

## Architecture

The backend follows a feature-based vertical-slice architecture.

```text
app/
├── core/
├── auth/
├── users/
├── transactions/
├── categories/
├── budgets/
├── dashboard/
└── analytics/
```

Each feature keeps its API schemas, routes, business logic, and database operations together.

## API Documentation

Interactive API documentation is available through Swagger UI when the application is running locally.

[Swagger UI](http://localhost:8000/docs)

## Running Locally

### Prerequisites

- Docker
- Docker Compose
- Git

### Setup

Clone the repository:

```bash
git clone https://github.com/sandra-simon/smartspend-backend.git
cd smartspend-backend
```

Create a `.env` file using `.env.example`, then start the application:

```bash
docker compose up -d --build
```

Apply the database migrations:

```bash
docker compose exec api alembic upgrade head
```

The API will be available at:

[http://localhost:8000](http://localhost:8000)

Swagger UI:

[http://localhost:8000/docs](http://localhost:8000/docs)

Mailpit:

[http://localhost:8025](http://localhost:8025)

## CI

GitHub Actions is used for continuous integration to automatically verify the application when changes are pushed to the repository.

## Project Status

Backend development is complete for the current API scope. The React frontend is being developed separately.