# SmartSpend — Backend API

The backend service for **SmartSpend**, a personal finance management application for tracking income and expenses, managing categories and monthly budgets, and analyzing spending through dashboards and analytics.

Built with FastAPI and PostgreSQL, the backend provides REST APIs for authentication, transaction management, category management, budgeting, and financial analytics.

## Tech Stack

- **Framework:** FastAPI, Python
- **Database:** PostgreSQL
- **ORM & Migrations:** SQLAlchemy, Alembic
- **Authentication:** JWT access and refresh tokens
- **Password Security:** Argon2 password hashing
- **Email:** SMTP-based email delivery
- **Containerization:** Docker, Docker Compose
- **CI:** GitHub Actions

## Features

- User registration, login, and authentication
- JWT access and refresh token support
- Password reset through email
- User profile and preference management
- Income and expense transaction management
- Transaction search, filtering, sorting, and pagination
- Custom income and expense categories
- Optional category-specific monthly budgets
- Dashboard summaries and expense breakdowns
- Financial analytics and spending trends
- Input validation and environment-based configuration

## Architecture

The backend follows a **feature-based vertical-slice architecture**, organizing application code by functional domain.

```text
app/
├── core/           # Shared configuration and infrastructure
├── auth/           # Authentication
├── users/          # User profiles and preferences
├── transactions/   # Income and expense transactions
├── categories/     # Category management
├── budgets/        # Budget management
├── dashboard/      # Dashboard summaries
└── analytics/      # Financial analytics
```

Each feature keeps its related API schemas, routes, business logic, and database operations organized together.

## API Documentation

When the application is running locally, interactive API documentation is available through Swagger UI:

**Swagger UI:** http://localhost:8000/docs

**OpenAPI schema:** http://localhost:8000/openapi.json

These are local development URLs, not publicly hosted API endpoints.

## Running Locally

### Prerequisites

- Git
- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/sandra-simon/smartspend-backend.git
cd smartspend-backend
```

### 2. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Fill in the required configuration values for the database, JWT authentication, SMTP email delivery, and frontend URL.

**Important:** Use your own local credentials and secrets. Never commit your `.env` file or expose production credentials.

### 3. Start the services

```bash
docker compose up -d --build
```

### 4. Apply database migrations

```bash
docker compose exec api alembic upgrade head
```

### 5. Access the API

- **API base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **Mailpit web interface:** http://localhost:8025

The URLs above assume the default local ports configured by the project.

## Email Configuration

SmartSpend supports SMTP-based email delivery for password-reset emails and other email workflows.

Configure the SMTP settings in your local `.env` file using `.env.example` as a reference.

For real email delivery, the application can be configured to use **Gmail SMTP**. Provide the required SMTP username, password, sender email address, and other configuration values through environment variables.

For Gmail accounts with two-step verification enabled, use a Google App Password where required. Do not commit real SMTP credentials or application passwords to Git.

### Local Email Testing with Mailpit

Mailpit is available as an optional development tool for capturing and inspecting outgoing emails locally without delivering them to real recipients.

When Mailpit is configured and running, open its web interface at:

http://localhost:8025

Use Gmail SMTP for actual email delivery and Mailpit for local testing. Configure the appropriate SMTP settings for the environment in which the application runs.

## Continuous Integration

GitHub Actions runs the configured CI workflow when changes are pushed to supported branches or pull requests are opened.

The current workflow checks that the application can be imported with its configured environment. This helps catch configuration and startup-import issues; it does not, by itself, constitute a comprehensive automated test suite.

## Frontend

The React frontend is maintained separately:

**[SmartSpend Frontend Repository](https://github.com/sandra-simon/smartspend-frontend)**

See the frontend repository for screenshots, application features, and the overall project overview.

## Author

**Sandra Simon**

- [GitHub](https://github.com/sandra-simon)
- [LinkedIn](https://www.linkedin.com/in/sandra-simon2301/)