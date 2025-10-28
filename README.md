# FastAPI Zero

A FastAPI-based REST API project with user authentication, todo management, and PostgreSQL database integration.

## Features

- User authentication with JWT tokens
- Todo management (CRUD operations)
- PostgreSQL database integration
- Docker support
- Automated testing
- CI/CD pipeline with GitHub Actions

## Technologies & Libraries

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Token authentication
- **Poetry**: Dependency management
- **pytest**: Testing framework
- **Docker**: Containerization
- **PostgreSQL**: Database

## Requirements

- Python 3.13+
- Poetry
- Docker and Docker Compose (optional)
- PostgreSQL (if not using Docker)

## Installation

1. Clone the repository
2. Install dependencies:
```sh
poetry install
```

3. Copy `.env_example` to `.env` and configure your environment variables:
```sh
cp .env_example .env
```

## Running the Application

### Using Docker

```sh
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Without Docker

1. Start a PostgreSQL database
2. Configure your `.env` file
3. Run database migrations:
```sh
poetry run alembic upgrade head
```

4. Start the application:
```sh
poetry run uvicorn fastapi_zero.app:app --reload
```

## Development Tasks

The project uses `taskipy` for common development tasks:

```sh
# Format code
poetry run task format

# Run linter
poetry run task lint

# Run tests
poetry run task test

# Run migrations
poetry run task migrate

# Generate new migration
poetry run task migrate_generate "migration_name"
```

## Testing

Tests are written using pytest. To run the test suite:

```sh
poetry run task test
```

This will:
1. Run linting checks
2. Execute all tests
3. Generate coverage report

## API Documentation

When running the application, API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
fastapi_zero/
├── app.py              # FastAPI application setup
├── database.py         # Database configuration
├── models/            # SQLAlchemy models
├── routers/           # API routes
├── schemas.py         # Pydantic models
├── security.py        # Authentication logic
└── settings.py        # Application settings

migrations/            # Alembic migrations
tests/                # Test suite
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_EXPIRE_IN_MINUTES`: Token expiration time (default: 30)

## CI/CD

The project includes a GitHub Actions workflow that:
- Runs on push and pull requests
- Executes the test suite
- Verifies code quality

## License

This project is open-sourced under the MIT license.