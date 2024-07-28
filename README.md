
# Django Task Manager

This is a Django-based task manager application that includes user authentication and task management functionalities.

## Prerequisites

- Python 3.x
- pip
- PostgreSQL
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/vinayfranklin123/tasks.git
cd tasks
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

You can install dependencies with:

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Setup

#### Install PostgreSQL

Follow the instructions to install PostgreSQL for your operating system:

- [PostgreSQL Downloads](https://www.postgresql.org/download/)

#### Create a PostgreSQL Database

```bash
# Access the PostgreSQL shell
psql -U postgres

# Inside the PostgreSQL shell, run the following commands:
CREATE DATABASE task_manager;
CREATE USER task_user WITH PASSWORD 'password';
ALTER ROLE task_user SET client_encoding TO 'utf8';
ALTER ROLE task_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE task_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE task_manager TO task_user;
\q
```

### 5. Configure Settings

Update the settings.py file in your Django project to include the database and other configurations:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'task_manager',
        'USER': 'task_user',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

### 6. Apply Migrations

```bash
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your superuser.

### 8. Run the Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`.

## Running Tests

To run the tests, use the following command:

```bash
python manage.py test
```

## API Endpoints

### User Authentication

- **Register**: `POST /auth/register/`
- **Login**: `POST /auth/login/`
- **Logout**: `POST /auth/logout/`

### Task Management

- **Create Task**: `POST /tasks/create/`
- **Update Task**: `PUT /tasks/update/<int:task_id>/`
- **Mark Task as Completed**: `POST /tasks/complete/<int:task_id>/`
- **Soft Delete Task**: `DELETE /tasks/delete/<int:task_id>/`
- **List Tasks**: `GET /tasks/list/`
