import pytest
from django.test import Client,RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from receipes.forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from receipes.models import Profile,Recipe,Rating,Comment,RecipeCollection,UserFollow,User,Notification
from receipes.forms import ProfileForm,RecipeForm,RatingForm,CommentForm,RecipeCollectionForm,AddRecipeToCollectionForm
from receipes.views import ProfileDetailView,UserRecipesView

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def register_url():
    return reverse('register')  # Adjust 'register' based on your URL configuration

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

@pytest.mark.django_db
def test_register_view_get(client, register_url):
    response = client.get(register_url)
    assert response.status_code == 200
    assert 'register.html' in [template.name for template in response.templates]
    assert isinstance(response.context['form'], CustomUserCreationForm)

#the submitted form data is invalid, specifically when the passwords do not match (password1 and password2).
@pytest.mark.django_db
def test_register_view_post_failure(client, register_url, user_data):
    invalid_data = user_data.copy()
    invalid_data['password2'] = 'differentpassword'
    
    response = client.post(register_url, invalid_data)
    assert response.status_code == 200
    assert 'register.html' in [template.name for template in response.templates]
    assert response.context['form'].has_error('password2')



@pytest.fixture
def login_url():
    return reverse('login')  # Adjust 'login' based on your URL configuration

@pytest.mark.django_db
def test_login_view_get(client, login_url):
    response = client.get(login_url)
    assert response.status_code == 200
    assert 'login.html' in [template.name for template in response.templates]
    assert isinstance(response.context['form'], AuthenticationForm)


@pytest.fixture
def profile_update_url():
    return reverse('profile_edit')  # Adjust 'profile_update' based on your URL configuration

@pytest.mark.django_db
def test_profile_update_view_get(client, profile_update_url, django_user_model):
    # Create a test user and profile
    user = django_user_model.objects.create_user(username='testuser', password='testpassword')
    profile = Profile.objects.create(user=user)
    
    # Login the test user
    client.login(username='testuser', password='testpassword')
    
    # Make a GET request to profile update view
    response = client.get(profile_update_url)
    
    # Assertions
    assert response.status_code == 200
    assert 'profile_form.html' in [template.name for template in response.templates]
    assert isinstance(response.context['form'], ProfileForm)
    assert response.context['profile'] == profile


#It prepares updated_data with the new bio text to be submitted through the POST request. This simulates the user updating their profile information.
@pytest.mark.django_db
def test_profile_update_view_post_success(client, profile_update_url):
    # Create a test user and profile
    user = get_user_model().objects.create_user(username='testuser', password='testpassword')
    profile = Profile.objects.create(user=user)
    
    # Login the test user
    client.login(username='testuser', password='testpassword')
    
    # Post profile update data
    updated_data = {
        'bio': 'Updated bio text',
        # Include other fields as necessary for ProfileForm
    }
    response = client.post(profile_update_url, updated_data, follow=True)
    
    # Assertions
    assert response.status_code == 200  # Should be 302 (redirect) if successful, 200 if form errors
    assert response.redirect_chain[0][0] == reverse('profile_view')  # Check if redirected to profile view page
    
    # Check messages in response
    assert 'Profile has been updated.' in [msg.message for msg in response.context['messages']]
    
    # Refresh profile instance from database and verify changes
    profile.refresh_from_db()
    assert profile.bio == updated_data['bio']


@pytest.fixture
def profile_detail_url():
    return reverse('profile_view')  # Adjust 'profile_detail' based on your URL configuration

@pytest.mark.django_db
def test_profile_detail_view(client, profile_detail_url, django_user_model):
    # Create a test user and profile
    user = django_user_model.objects.create_user(username='testuser', password='testpassword')
    profile = Profile.objects.create(user=user, bio='Test bio')  # Create a profile with some data
    
    # Login the test user
    client.login(username='testuser', password='testpassword')
    
    # Make a GET request to profile detail view
    response = client.get(profile_detail_url)
    
    # Assertions
    assert response.status_code == 200
    assert 'profile_view.html' in [template.name for template in response.templates]
    assert response.context['profile'] == profile

@pytest.fixture
def home_url():
    return reverse('home')  # Adjust 'home' based on your URL configuration


@pytest.mark.django_db
def test_home_view_get(client, home_url):
    # Create a test user
    User = get_user_model()
    user = User.objects.create_user(username='testuser', password='testpassword')

    # Create a test recipe with required fields including author
    recipe = Recipe.objects.create(
        title='Pasta Carbonara',
        ingredients='Pasta, eggs, cheese',
        instructions='Cook pasta, mix with eggs and cheese, serve hot.',
        category='dinner',
        cooking_time=30,
        author=user  # Assign the created user as the author
    )

    # Make a GET request to home view
    response = client.get(home_url, {'search_query': 'Pasta'})

    # Assertions
    assert response.status_code == 200
    assert 'home.html' in [template.name for template in response.templates]
    assert 'Pasta Carbonara' in str(response.content)

from django.urls import reverse_lazy


@pytest.mark.django_db
def test_logout_view():
    # Create a test user and log them in
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')

    # Make a GET request to logout
    response = client.get(reverse_lazy('logout'), follow=True)

    # Assertions
    assert response.status_code == 200  # Assuming logout view returns 200 on success
    assert response.redirect_chain[-1][0] == reverse_lazy('home')  # Check redirection URL

    # Check if logout message is set
    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert "You have been logged out." in [msg.message for msg in messages]


# #for create recipe
    
@pytest.fixture
def login_user(client):
    user = User.objects.create_user(username='testuser', password='testpassword')
    profile = Profile.objects.create(user=user)  # Create a profile for the user
    client.login(username='testuser', password='testpassword')
    return user

@pytest.mark.django_db
def test_create_recipe_view_post_success(client, login_user):
    url = reverse('create_recipe')  # Adjust based on your URL configuration
    initial_recipe_count = Recipe.objects.count()
    post_data = {
        'title': 'Test Recipe',
        'ingredients': 'Ingredient 1, Ingredient 2',
        'instructions': 'Step 1, Step 2',
        'category': 'breakfast',
        'cooking_time': 30,
    }
    
    response = client.post(url, post_data, follow=True)
    
    assert response.status_code == 200  # Should be 302 (redirect) if successful, 200 if form errors
    assert Recipe.objects.count() == initial_recipe_count + 1
    
    # Adjust this assertion based on your redirect URL after successful recipe creation
    assert response.redirect_chain[0][0] == reverse('recipe_detail', kwargs={'pk': Recipe.objects.last().pk})
    
@pytest.mark.django_db
def test_create_recipe_view_post_failure(client, login_user):
    url = reverse('create_recipe')  # Adjust based on your URL configuration
    initial_recipe_count = Recipe.objects.count()
    post_data = {
        'title': '',  # Invalid data to trigger form validation error
        'ingredients': 'Ingredient 1, Ingredient 2',
        'instructions': 'Step 1, Step 2',
        'category': 'breakfast',
        'cooking_time': 30,
    }
    
    response = client.post(url, post_data, follow=True)
    
    assert response.status_code == 200  # Should stay on the same page with errors
    assert Recipe.objects.count() == initial_recipe_count  # No new recipe should be created
    assert 'recipe_form.html' in [template.name for template in response.templates]
    assert 'This field is required.' in str(response.content)  # Adjust based on your form validation error message

#update recipe
    
@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def another_user(db):
    User = get_user_model()
    return User.objects.create_user(username='anotheruser', password='anotherpassword')

@pytest.fixture
def recipe(user):
    return Recipe.objects.create(
        title='Pasta Carbonara',
        ingredients='Pasta, eggs, cheese',
        instructions='Cook pasta, mix with eggs and cheese, serve hot.',
        category='dinner',
        cooking_time=30,
        author=user
    )

@pytest.fixture
def client_logged_in(user):
    client = Client()
    client.login(username='testuser', password='testpassword')
    return client


@pytest.mark.django_db
def test_update_recipe_view_get(client_logged_in, recipe):
    # URL for the recipe update view
    url = reverse('update_recipe', kwargs={'pk': recipe.pk})
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 200
    assert 'recipe_form.html' in [template.name for template in response.templates]
    assert isinstance(response.context['form'], RecipeForm)
    assert response.context['form'].instance == recipe

@pytest.mark.django_db
def test_update_recipe_view_post_valid(client_logged_in, recipe):
    # URL for the recipe update view
    url = reverse('update_recipe', kwargs={'pk': recipe.pk})
    
    # Valid form data
    data = {
        'title': 'Updated Pasta Carbonara',
        'ingredients': 'Pasta, eggs, cheese, bacon',
        'instructions': 'Cook pasta, mix with eggs, cheese, and bacon, serve hot.',
        'category': 'dinner',
        'cooking_time': 35,
    }
    
    # Make POST request
    response = client_logged_in.post(url, data)
    
    # Refresh the recipe instance from the database
    recipe.refresh_from_db()
    
    # Assertions
    assert response.status_code == 302
    assert response.url == reverse('recipe_detail', kwargs={'pk': recipe.pk})
    assert recipe.title == 'Updated Pasta Carbonara'
    assert recipe.ingredients == 'Pasta, eggs, cheese, bacon'
    assert recipe.instructions == 'Cook pasta, mix with eggs, cheese, and bacon, serve hot.'
    assert recipe.cooking_time == 35

@pytest.mark.django_db
def test_update_recipe_view_post_invalid(client_logged_in, recipe):
    # URL for the recipe update view
    url = reverse('update_recipe', kwargs={'pk': recipe.pk})
    
    # Invalid form data (e.g., missing title)
    data = {
        'title': '',
        'ingredients': 'Pasta, eggs, cheese, bacon',
        'instructions': 'Cook pasta, mix with eggs, cheese, and bacon, serve hot.',
        'category': 'dinner',
        'cooking_time': 35,
    }
    
    # Make POST request
    response = client_logged_in.post(url, data)
    
    # Assertions
    assert response.status_code == 200
    assert 'recipe_form.html' in [template.name for template in response.templates]
    assert isinstance(response.context['form'], RecipeForm)
    assert response.context['form'].errors



#delete recipe
    
@pytest.mark.django_db
def test_delete_recipe_view_get_author(client_logged_in, recipe):
    # URL for the recipe delete view
    url = reverse('delete_recipe', kwargs={'pk': recipe.pk})
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 302
    assert response.url == reverse('user_recipes')
    assert not Recipe.objects.filter(pk=recipe.pk).exists()

@pytest.mark.django_db
def test_delete_recipe_view_get_non_author(client_logged_in, another_user, recipe):
    # Log in as another user
    client_logged_in.logout()
    client_logged_in.login(username='anotheruser', password='anotherpassword')

    # URL for the recipe delete view
    url = reverse('delete_recipe', kwargs={'pk': recipe.pk})
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 302
    assert response.url == reverse('recipe_detail', kwargs={'pk': recipe.pk})
    assert Recipe.objects.filter(pk=recipe.pk).exists()


#user recipe view
    
@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def another_user(db):
    User = get_user_model()
    return User.objects.create_user(username='anotheruser', password='anotherpassword')

@pytest.fixture
def recipes(user):
    return [
        Recipe.objects.create(
            title='Pasta Carbonara',
            ingredients='Pasta, eggs, cheese',
            instructions='Cook pasta, mix with eggs and cheese, serve hot.',
            category='dinner',
            cooking_time=30,
            author=user
        ),
        Recipe.objects.create(
            title='Chicken Curry',
            ingredients='Chicken, curry spices',
            instructions='Cook chicken with curry spices, serve with rice.',
            category='dinner',
            cooking_time=40,
            author=user
        )
    ]

@pytest.fixture
def client_logged_in(user):
    client = Client()
    client.login(username='testuser', password='testpassword')
    return client

@pytest.mark.django_db
def test_user_recipes_view_get(client_logged_in, recipes):
    # URL for the user recipes view
    url = reverse('user_recipes')
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 200
    assert 'user_recipes.html' in [template.name for template in response.templates]
    assert len(response.context['recipes']) == len(recipes)
    for recipe in recipes:
        assert recipe in response.context['recipes']

@pytest.mark.django_db
def test_user_recipes_view_get_no_recipes(client_logged_in):
    # URL for the user recipes view
    url = reverse('user_recipes')
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 200
    assert 'user_recipes.html' in [template.name for template in response.templates]
    assert len(response.context['recipes']) == 0

@pytest.mark.django_db
def test_user_recipes_view_get_another_user(client_logged_in, another_user):
    # URL for the user recipes view
    url = reverse('user_recipes')
    
    # Create recipes for another user
    Recipe.objects.create(
        title='Beef Stew',
        ingredients='Beef, vegetables',
        instructions='Cook beef with vegetables, serve hot.',
        category='dinner',
        cooking_time=90,
        author=another_user
    )
    
    # Make GET request
    response = client_logged_in.get(url)
    
    # Assertions
    assert response.status_code == 200
    assert 'user_recipes.html' in [template.name for template in response.templates]
    assert len(response.context['recipes']) == 0


#update comment

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from mixer.backend.django import mixer
from receipes.models import Comment  # Adjust with your actual app and model names

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def comment(user):
    return mixer.blend(Comment, author=user)

@pytest.mark.django_db
def test_update_comment_view_get(client, user, comment):
    client.force_login(user)
    response = client.get(reverse('update_comment', kwargs={'comment_id': comment.pk}))
    assert response.status_code == 200
    assert 'comment_form' in response.context
    assert response.context['comment_form'].instance == comment

#delete recipe from collection
    
@pytest.mark.django_db
def test_delete_recipe_from_collection_get():
    # Create a user
    user = User.objects.create_user(username='testuser', password='12345')

    # Log in the user
    client = Client()
    client.login(username='testuser', password='12345')

    # Create a recipe and a collection
    recipe = Recipe.objects.create(title='Test Recipe', ingredients='Test Ingredients', instructions='Test Instructions', category='Test Category', cooking_time=10, author=user)
    collection = RecipeCollection.objects.create(name='Test Collection', user=user)
    collection.recipes.add(recipe)

    # Get the URL for the view
    url = reverse('delete_recipe_from_collection', args=[collection.id, recipe.id])

    # Make a GET request to the view
    response = client.get(url)

    # Check that the response is 200 OK and the correct template is used
    assert response.status_code == 200
    assert 'delete_recipe_from_collection.html' in (t.name for t in response.templates)

    # Check that the collection and recipe are in the context
    assert response.context['collection'] == collection
    assert response.context['recipe'] == recipe

@pytest.mark.django_db
def test_delete_recipe_from_collection_post():
    # Create a user
    user = User.objects.create_user(username='testuser', password='12345')

    # Log in the user
    client = Client()
    client.login(username='testuser', password='12345')

    # Create a recipe and a collection
    recipe = Recipe.objects.create(title='Test Recipe', ingredients='Test Ingredients', instructions='Test Instructions', category='Test Category', cooking_time=10, author=user)
    collection = RecipeCollection.objects.create(name='Test Collection', user=user)
    collection.recipes.add(recipe)

    # Get the URL for the view
    url = reverse('delete_recipe_from_collection', args=[collection.id, recipe.id])

    # Make a POST request to the view
    response = client.post(url)

    # Check that the response is a redirect
    assert response.status_code == 302
    assert response.url == reverse('collection_detail', args=[collection.id])

    # Check that the recipe has been removed from the collection
    collection.refresh_from_db()
    assert recipe not in collection.recipes.all()



