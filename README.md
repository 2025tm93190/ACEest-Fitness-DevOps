# ACEest Fitness & Gym

A responsive Flask web application for managing gym members and workout sessions. The project includes SQLite persistence, automated tests, Docker packaging, Jenkins pipeline automation, and GitHub Actions CI.

## Features

- Responsive dashboard with member and workout summary statistics
- Add, search, view, edit, and delete members
- Log workouts with duration, date, estimated calories, and notes
- Per-member workout history and totals
- Calorie calculator using a Mifflin–St Jeor estimate and activity multiplier
- Health-check endpoint at `/health`
- Pytest suite, Docker image, Jenkins pipeline, and GitHub Actions workflow

## Requirements

- Python 3.12 or newer supported by Flask
- Docker Desktop for container build/run
- Git for version control

## Run locally on Windows

Open Command Prompt in the project directory:

```bat
"C:\Users\Nivedhitha\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt
"C:\Users\Nivedhitha\AppData\Local\Programs\Python\Python314\python.exe" app.py
```

Then open http://127.0.0.1:5000 in your browser. If Python is available through the `python` command, you can use `python -m pip` and `python app.py` instead.

## Run tests

```bat
"C:\Users\Nivedhitha\AppData\Local\Programs\Python\Python314\python.exe" -m pytest -v
```

## Docker

Make sure Docker Desktop is running, then from the project folder:

```bat
docker build -t aceest-fitness .
docker run --rm -p 5000:5000 -e PORT=5000 -v aceest-data:/app/instance aceest-fitness
```

Open http://127.0.0.1:5000. The named Docker volume keeps the SQLite database in `/app/instance` between container runs.

Run the tests in the image:

```bat
docker run --rm aceest-fitness python -m pytest -v
```

## Jenkins

1. Install the Jenkins Pipeline and Git plugins.
2. Ensure Jenkins can run Git, Python, and Docker. Docker Desktop must be running and accessible to the Jenkins service.
3. Create a Pipeline job configured as **Pipeline script from SCM**.
4. Choose Git and enter your own repository URL and branch (`main`).
5. Set the script path to `Jenkinsfile`.
6. Save and select **Build Now**.

**Windows note:** The included Jenkinsfile uses the Python executable path from the development machine. If Jenkins runs under another Windows account or on another computer, update the path or configure Python on that agent and use `python -m ...`. The agent also needs permission to execute Docker commands.

## GitHub Actions

The workflow at `.github/workflows/main.yml` runs when code is pushed to `main` or a pull request targets `main`. It installs dependencies, checks Python syntax, runs tests, builds the Docker image, and runs tests inside that image.

## Project structure

```text
app.py
requirements.txt
templates/
static/css/style.css
static/js/app.js
tests/test_app.py
Dockerfile
.dockerignore
Jenkinsfile
.github/workflows/main.yml
README.md
```

## Data and security notes

- Member and workout records are stored in SQLite in the `instance` directory by default.
- This is an educational project. It does not include authentication or authorization, so do not expose it publicly with real member data.
- Set a strong `SECRET_KEY` environment variable for deployments.
- Calorie values are estimates for general information only, not medical advice.
