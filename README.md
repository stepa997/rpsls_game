# RPSLS Game Project

This project includes a backend (FastAPI), frontend (React), and a PostgreSQL database, all orchestrated via Docker Compose.

---

## Project Structure

- `rpsls_game_api/` - Backend API (FastAPI)  
- `rpsls_game_frontend/` - Frontend (React)  
- `docker-compose.yaml` - Orchestrates the entire system (database, API, frontend)

---

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. **Create a `.env` file in the root directory (same level as docker-compose.yaml) with the following content:**

```bash
DB_USER is database username for connecting to PostgreSQL.
DB_PASSWORD is password for the database user.
DB_HOST is host address of the PostgreSQL server (e.g., localhost or Docker service name)
DB_NAME is name of the database to connect to
DB_PORT is the port your local machine uses to connect to the PostgreSQL container
API_PORT is the port on which the FastAPI backend will be exposed
FRONTEND_PORT is the port on which the React frontend will be exposed
```

3. **Start the project with Docker Compose:**

```bash
docker-compose up -d --build
```
This command will build and start the PostgreSQL database, the FastAPI backend, and the React frontend in separate Docker containers.

## Access the application
Backend API: http://localhost:${API_PORT}

Frontend UI: http://localhost:${FRONTEND_PORT}

## Additional Information
The database will be initialized automatically on the first run.

Backend and frontend communicate via Docker internal networking.

## License & Contact
Feel free to use and modify this project.
For questions, reach out via `djolestepa997@gmail` or GitHub profile `stepa997`.

