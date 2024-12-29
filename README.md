# Chair Backend

Welcome to the Chair project API repository! This API serves as the backbone, providing essential functionality and data processing to ensure a seamless user experience.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Table of Contents
1. [Settings](#settings)
2. [Getting Started](#getting-started)
   - [Running Project without Docker](#running-project-without-docker)
   - [Running Project with Docker](#running-project-with-docker)
3. [Common Setup](#common-setup)

## Settings

For detailed settings, refer to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Getting Started

Follow these instructions to set up and run the backend API on your local machine.

### Common Setup

1. **Environment Setup:**
   - Copy the example environment file:  
     ```sh
     cp .env.example .env
     ```
   - Update the environment variables as needed.

## Running Project Without Docker

### Prerequisites 

Ensure the following are installed on your machine:
- Python
- Virtualenv

### Setting Up the Virtual Environment

1. **Install virtualenv:**  
   ```sh
   pip install virtualenv
   ```

2. **Create a virtual environment:**  
   ```sh
   virtualenv env
   ```

3. **Activate the virtual environment:**  
   - On Windows:  
     ```sh
     env\Scripts\activate
     ```
   - On macOS/Linux:  
     ```sh
     source env/bin/activate
     ```

4. **Install the required packages:**  
   ```sh
   pip install -r requirements.txt
   ```

5. **Run the development server:**  
   ```sh
   python manage.py runserver
   ```

### Creating Superuser

1. Create a superuser:  
   ```sh
   python manage.py createsuperuser
   ```

### Migrations

1. **Make migrations:**  
   ```sh
   python manage.py makemigrations
   ```

2. **Apply migrations:**  
   ```sh
   python manage.py migrate
   ```

3. **For specific migrations:**  
   ```sh
   python manage.py migrate <app_name> <migration_name>
   ```

### Before Committing Code

1. Update the requirements file:  
   ```sh
   pip freeze > requirements.txt
   ```

*Note: Ensure that these commands are run from the same directory as `manage.py`.*

## Running Project with Docker

### Prerequisites

Ensure the following are installed:
- Docker (Latest version)
- Docker Compose (Latest version)

### Additional Environment Variables

1. Set the project name and other variables:
   ```sh
   PROJECT=<project_name>
   REQUIREMENT_FILE=<requirement_file_path>
   REDIS_URL=redis://redis:6379
   ```

2. For local development with a local database, set:
   ```sh
   LOCAL_DB_HOST=host.docker.internal
   ```

### Running in Development

1. **Build Docker images:**  
   (Only necessary for the first time or when new packages are added)  
   ```sh
   docker-compose -f docker-compose-dev.yaml build
   ```

2. **Start the development environment:**  
   ```sh
   docker-compose -f docker-compose-dev.yaml up -d
   ```

3. **Stop and remove containers:**  
   ```sh
   docker-compose -f docker-compose-dev.yaml down
   ```

### Creating Superuser in Docker

1. List the running containers:  
   ```sh
   docker ps
   ```

2. Access the container's shell:  
   ```sh
   docker exec -it <container_id_or_name> /bin/bash
   ```

3. Create the superuser:  
   ```sh
   python manage.py createsuperuser
   ```

### Running in Production

1. **Build Docker images:**  
   ```sh
   docker-compose -f docker-compose-prod.yaml build
   ```

2. **Start the production environment:**  
   ```sh
   docker-compose -f docker-compose-prod.yaml up -d
   ```

3. **Stop Docker containers:**  
   ```sh
   docker-compose -f docker-compose-prod.yaml stop
   ```

4. **Remove containers:**  
   ```sh
   docker-compose -f docker-compose-prod.yaml down
   ```
