# receipe_assignment

# Recipe Sharing Platform

## Objective

Create a Recipe Sharing Platform where users can share, browse, and save recipes. The system includes user authentication, recipe management, and social features like comments and ratings. The backend is implemented using Django.

## Requirements

### 1. User Authentication and Authorization
- Implement user registration and login functionality.
- Allow users to update their profiles.
- Secure endpoints using session-based authentication.

### 2. Recipe Management
- Allow users to create, read, update, and delete recipes.
- Each recipe has the following attributes:
  - Title
  - Ingredients
  - Instructions
  - Category (e.g., Breakfast, Lunch, Dinner)
  - Cooking time
  - Author (user who created the recipe)
- Display a list of all recipes with pagination and search functionality.

### 3. Comments and Ratings
- Allow users to comment on and rate recipes.
- Display average ratings and comments for each recipe.

### 4. Recipe Collections
- Allow users to save recipes to their personal collections.
- Organize saved recipes into custom collections (e.g., Favorite Desserts).

### 5. Admin Panel
- Implement an admin panel to manage users and recipes.
- Allow admins to view popular recipes and user activity.

### 6. Testing
- Write unit and integration tests for the key functionalities.

## Optional Features (for bonus points)
- Implement a feature to upload and display images for recipes.
- Add a feature for users to follow other users and see their recipes.
- Create a simple frontend using HTML, CSS, and JS.

## Message Broker Integration
- **RabbitMQ/Kombu**: Integrate RabbitMQ for handling asynchronous tasks such as sending notifications.
- **Task Queue**: Implement a task queue to manage background tasks efficiently.
- **Real-Time Updates**: Use message brokers to provide real-time updates to users (e.g., live notifications of comments and ratings).

## Setup and Running the Project

### Prerequisites
- Python 3.x
- Django
- RabbitMQ
- Celery

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/sonalimohantaneosoftmail/receipe_assignment2.git
    cd receipe_assignment2
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv 
    or 
    virtualenv venv --python=python3.11
    
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create a superuser for accessing the admin panel:
    ```sh
    python manage.py createsuperuser
    ```

### Running the Project

1. Start the Django development server:
    ```sh
    python manage.py runserver
    ```

2. Start RabbitMQ server:
    ```sh
    systemctl start rabbitmq-server
    ```

3. Start Celery worker:
    ```sh
    celery -A myproject worker -l info
    ```

### Running Tests

To run the tests, use the following command:
```sh
pytest

