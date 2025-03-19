# Django - Backend Setup Guide

## Prerequisites
- Python 3.9 or later installed
- pip (Python package manager)
- venv (included with Python 3.9+)

## Setting Up the Project

### 1. Create a Virtual Environment
* Open your terminal, navigate to your project directory, and run:

    `python3 -m venv venv`

### 2. Activate the Virtual Environment
* On macOS/Linux:
`source venv/bin/activate`

* On Windows (Command Prompt):
`venv\Scripts\activate`

* Once activated, your terminal prompt will show a prefix (e.g., (venv)).

### 3. Install Django
* With the virtual environment activated, install Django:

    `pip3 install django`

### 4. Start a Django Project
* Create your Django project (here we name it placement_backend):

    `django-admin startproject placemate`
    
### 5. Create a Django App
* `python3 manage.py startapp placemate_app`
This command creates a new folder named placement containing files such as models.py, views.py, admin.py, and others, which will hold your app-specific code.

### 6. Run Initial Migrations
* Set up the database by applying initial migrations:
    `python3 manage.py migrate`

### 7. Run the Development Server
* Start the development server to test your project:

    `python3 manage.py runserver`
Open your browser and navigate to http://127.0.0.1:8000/ to see your Django project in action.

## Additional Configuration
Dependency Management: Once all required packages are installed, generate a requirements.txt file:
`pip3 freeze > requirements.txt`


export PATH="/Library/PostgreSQL/17/bin:$PATH"
echo 'export PATH="/Library/PostgreSQL/17/bin:$PATH"' >> diretory to venv/activate
reload