from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Recipe, Profile, RecipeCollection, UserFollow, Notification, User
from .models import Comment, Rating


from .forms import (
    RecipeForm,
    CommentForm,
    RatingForm,
    ProfileForm,
    RecipeCollectionForm,
    RecipeCollectionFormWithName,
    AddRecipeToCollectionForm,
)
from django.db.models import Avg
from django.views.generic.edit import FormView
from django.views.generic import ListView, UpdateView, DetailView
from django.views import View
from django.urls import reverse_lazy


import logging

logger = logging.getLogger(__name__)



# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from django.core.paginator import Paginator
from receipes.tasks import send_notification
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
import logging


logger = logging.getLogger(__name__)


class RegisterView(FormView):
    """
    A view to handle user registration using a custom user creation form.
    On successful registration, the user is authenticated and logged in.

    Attributes:
        template_name (str): The path to the template used to render the registration form.
        form_class (FormClass): The form class used for user registration.
        success_url (str): The URL to redirect to on successful registration.
    """

    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = "/home/"

    def form_valid(self, form):
        """
        If the form is valid, save the user, authenticate, and log them in.

        Args:
            form (Form): The valid form instance.

        Returns:
            HttpResponseRedirect: Redirects to the success URL on successful login.
        """
        try:
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(self.request, user)
                self.request.session["user_id"] = user.id
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"An error occurred during registration: {e}")
            return render(self.request, self.template_name, {"form": form})

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and renders the registration form.

        Args:
            request (HttpRequest): The GET request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The rendered template response.
        """
        try:
            form = self.form_class()
            return render(request, self.template_name, {"form": form})
        except Exception as e:
            messages.error(request, f"An error occurred while loading the form: {e}")
            return render(request, self.template_name, {"form": None})


class LoginView(View):
    """
    View for user login.

    GET: Renders the login form.
    POST: Handles form submission, authenticates user, and logs them in if credentials are valid.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the login form.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Rendered login form template.
        """
        form = AuthenticationForm()
        return render(request, "login.html", {"form": form})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to process user login.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: Redirects to home page on successful login or renders login form with error messages.
        """
        form = AuthenticationForm(request, request.POST)
        try:
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    request.session["user_id"] = user.id  # Store user ID in session
                    return redirect("home")
                else:
                    messages.error(request, "Invalid username or password.")
            else:
                messages.error(request, "Invalid username or password.")
        except Exception as e:
            logger.error(f"Error in LoginView POST method: {e}")
            messages.error(request, "An error occurred during login. Please try again later.")

        return render(request, "login.html", {"form": form})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile.

    Attributes:
        model (Profile): The model to update.
        form_class (ProfileForm): The form class to use for updating profile data.
        template_name (str): The template to render for updating profile.
        context_object_name (str): The context variable name for the profile object.
    """

    model = Profile
    form_class = ProfileForm
    template_name = "profile_form.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Retrieve the profile object for the current user.

        Args:
            queryset (QuerySet, optional): The queryset from which to retrieve the profile. Defaults to None.

        Returns:
            Profile: The profile object associated with the current user.
        """
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        self.created = created  # Store the created flag to use in form_valid
        return profile

    def form_valid(self, form):
        """
        Process the form submission when it is valid.

        Args:
            form (ProfileForm): The validated form instance.

        Returns:
            HttpResponse: Redirects to success URL after saving the profile updates.
        """
        try:
            profile = form.save(commit=False)
            if self.created:
                messages.success(
                    self.request, "Profile has been created and saved in the database."
                )
            elif "bio" in form.changed_data:
                messages.success(self.request, "Profile has been updated.")
            else:
                messages.info(self.request, "No changes detected.")
            profile.save()
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error in ProfileUpdateView form_valid method: {e}")
            messages.error(self.request, "An error occurred while saving your profile.")
            return super().form_invalid(form)

    def get_success_url(self):
        """
        Get the URL to redirect to after successfully updating the profile.

        Returns:
            str: The URL path to redirect to.
        """
        return reverse_lazy("profile_view")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying user profile details.

    Attributes:
        model (Profile): The model to retrieve profile details.
        template_name (str): The template to render for displaying profile details.
        context_object_name (str): The context variable name for the profile object.
    """

    model = Profile
    template_name = "profile_view.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Retrieve the profile object for the current user.

        Args:
            queryset (QuerySet, optional): The queryset from which to retrieve the profile. Defaults to None.

        Returns:
            Profile: The profile object associated with the current user.
        """
        try:
            profile, created = Profile.objects.get_or_create(user=self.request.user)
            return profile
        except Exception as e:
            logger.error(f"Error in ProfileDetailView get_object method: {e}")
            # Handle exception appropriately, such as redirecting to an error page or displaying a message.
            raise  # Re-raise the exception for debugging purposes or to handle it in a higher level.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object().user
        context['follower_count'] = UserFollow.objects.filter(followed=profile_user).count()
        context['following_count'] = UserFollow.objects.filter(follower=profile_user).count()
        return context
    


class HomeView(ListView):
    """
    View for displaying a list of recipes filtered by search query.

    Attributes:
        model (Recipe): The model to retrieve recipes.
        template_name (str): The template to render for displaying recipes.
        context_object_name (str): The context variable name for the queryset of recipes.
        paginate_by (int): Number of recipes to display per page.
    """

    model = Recipe
    template_name = "home.html"
    context_object_name = "recipe"
    paginate_by = 2  # 2 recipes per page

    def get_queryset(self):
        """
        Get the queryset of recipes optionally filtered by search query.

        Returns:
            QuerySet: The filtered queryset of recipes.
        """
        try:
            queryset = super().get_queryset()
            search_query = self.request.GET.get("search_query")

            if search_query:
                queryset = queryset.filter(title__icontains=search_query) | queryset.filter(
                    ingredients__icontains=search_query
                )

            return queryset.order_by('title')  #have returned queryset but now added order_by('title') to avoid this error Django raises an UnorderedObjectListWarning to inform you that pagination might yield inconsistent results in testcases.
        except Exception as e:
            logger.error(f"Error in HomeView get_queryset method: {e}")
            # Handle exception appropriately, such as redirecting to an error page or displaying a message.
            raise  # Re-raise the exception for debugging purposes or to handle it in a higher level.



class LogoutView(View):
    """
    View for logging out a user.

    Attributes:
        None
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to logout the authenticated user.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the home page after logout.
        """
        try:
            if request.user.is_authenticated:
                # Clear user-related session variables upon logout
                request.session.flush()

                # Alternatively, clear specific session keys if needed:
                # if request.user.is_authenticated:
                #     del request.session['user_id']

                logout(request)
                messages.info(request, "You have been logged out.")
        except Exception as e:
            logger.error(f"Error in LogoutView get method: {e}")
            # Handle exception appropriately, such as redirecting to an error page or displaying a message.
            raise  # Re-raise the exception for debugging purposes or to handle it in a higher level.

        return redirect(reverse_lazy("home"))



class CreateRecipeView(LoginRequiredMixin, View):
    """
    View for creating a new recipe.

    Attributes:
        login_url (str): URL to redirect if user is not logged in.
    """

    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to display the recipe creation form.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: Rendered recipe creation form template.
        """
        form = RecipeForm()
        return render(request, "recipe_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to process recipe creation.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: Redirects to recipe detail page on successful creation or renders form with errors.
        """
        form = RecipeForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.author = request.user
                recipe.save()
                return redirect("recipe_detail", pk=recipe.pk)
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            messages.error(request, "An error occurred while creating the recipe. Please try again later.")

        return render(request, "recipe_form.html", {"form": form})


class UpdateRecipeView(LoginRequiredMixin, View):
    """
    View for updating an existing recipe.

    Attributes:
        login_url (str): URL to redirect if user is not logged in.
    """

    login_url = "/login/"

    def get(self, request, pk):
        """
        Handle GET request to display the recipe update form.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): Primary key of the recipe to update.

        Returns:
            HttpResponse: Rendered recipe update form template.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        form = RecipeForm(instance=recipe)
        return render(request, "recipe_form.html", {"form": form})

    def post(self, request, pk):
        """
        Handle POST request to process recipe update.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): Primary key of the recipe to update.

        Returns:
            HttpResponse: Redirects to recipe detail page on successful update or renders form with errors.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        try:
            if form.is_valid():
                form.save()
                return redirect("recipe_detail", pk=recipe.pk)
        except Exception as e:
            logger.error(f"Error updating recipe (ID: {pk}): {e}")
            messages.error(request, "An error occurred while updating the recipe. Please try again later.")

        return render(request, "recipe_form.html", {"form": form})


class DeleteRecipeView(LoginRequiredMixin, View):
    """
    View for deleting a recipe.

    Attributes:
        login_url (str): URL to redirect if user is not logged in.
    """

    login_url = "/login/"

    def get(self, request, pk):
        """
        Handle GET request to delete a recipe.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): Primary key of the recipe to delete.

        Returns:
            HttpResponse: Redirects to user's recipe list or recipe detail page based on deletion success.
        """
        try:
            recipe = get_object_or_404(Recipe, pk=pk)
            if request.user == recipe.author:
                recipe.delete()
                return redirect("user_recipes")
            else:
                # Optionally, you can add a message if the user tries to delete someone else's recipe
                return redirect("recipe_detail", pk=pk)
        except Exception as e:
            logger.error(f"Error deleting recipe (ID: {pk}): {e}")
            messages.error(request, "An error occurred while deleting the recipe. Please try again later.")
            return redirect("recipe_detail", pk=pk)



class UserRecipesView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of recipes created by the logged-in user.

    Attributes:
        login_url (str): URL to redirect if the user is not logged in.
        model (Model): The model that this view will operate upon.
        template_name (str): The path to the template used to render the recipes list.
    """

    login_url = "/login/"
    model = Recipe
    template_name = "user_recipes.html"
    context_object_name = "recipes"

    def get_queryset(self):
        """
        Override the default get_queryset method to filter recipes by the logged-in user.

        Returns:
            QuerySet: A queryset of recipes authored by the logged-in user.
        """
        try:
            return Recipe.objects.filter(author=self.request.user)
        except Exception as e:
            logger.error(f"Error fetching recipes for user {self.request.user.id}: {e}")
            return Recipe.objects.none()

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to display the list of user's recipes.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered user recipes list template.
        """
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error rendering user recipes for user {request.user.id}: {e}")
            return render(request, self.template_name, {"recipes": Recipe.objects.none()})


        
@login_required
def add_recipe_to_collection(request, recipe_id):
    """
    View function to add a recipe to a user's collection.

    Args:
        request (HttpRequest): The HTTP request object.
        recipe_id (int): ID of the recipe to add to a collection.

    Returns:
        HttpResponse: Rendered form template on GET request, redirects to home on successful POST, or renders form with errors.
    """
    try:
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == "POST":
            form = AddRecipeToCollectionForm(request.POST, user=request.user)
            if form.is_valid():
                collection = form.cleaned_data["collection"]
                collection.recipes.add(recipe)
                return redirect("home")
        else:
            form = AddRecipeToCollectionForm(user=request.user)

    except Recipe.DoesNotExist:
        logger.error(f"Recipe with ID {recipe_id} does not exist.")
        return redirect("home")  # Redirect to home page if recipe does not exist

    except Exception as e:
        logger.error(f"Error adding recipe (ID: {recipe_id}) to collection: {e}")
        form = AddRecipeToCollectionForm(user=request.user)
        # You can customize the error message displayed to the user here
        # For simplicity, let's redirect to home page with a generic error message
        return redirect("home")

    return render(request, "add_recipe_to_collection.html", {"form": form, "recipe": recipe})
        


@login_required
def delete_recipe_from_collection(request, collection_id, recipe_id):
    collection = get_object_or_404(
        RecipeCollection, pk=collection_id, user=request.user
    )
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == "POST":
        collection.recipes.remove(recipe)
        return redirect("collection_detail", collection_id=collection_id)
    return render(
        request,
        "delete_recipe_from_collection.html",
        {"collection": collection, "recipe": recipe},
    )


@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(
        RecipeCollection, pk=collection_id, user=request.user
    )
    if request.method == "POST":
        collection.delete()
        return redirect("collection_list")
    return render(request, "delete_collection.html", {"collection": collection})


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, pk=user_id)
    user_follow, created = UserFollow.objects.get_or_create(
        follower=request.user, followed=user_to_follow
    )
    if created:
        # Notify the recipe author
        send_notification.delay(
            recipient_id=user_to_follow.id,
            # sender_id=request.user.id,
            message=f"Hello {user_to_follow.username},\n\n{request.user.username} has started following you.",
        )
    return redirect("user_profile", user_id=user_id)


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, pk=user_id)
    UserFollow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
    return redirect("user_profile", user_id=user_id)



@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    user_recipes = Recipe.objects.filter(author=profile_user)
    following = UserFollow.objects.filter(
        follower=request.user, followed=profile_user
    ).exists()

    follower_count = UserFollow.objects.filter(followed=profile_user).count()
    following_count = UserFollow.objects.filter(follower=profile_user).count()

    context = {
        "profile_user": profile_user,
        "user_recipes": user_recipes,
        "following": following,
        "follower_count": follower_count,
        "following_count": following_count,
    }
    return render(request, "user_profile.html", context)


@login_required
def user_following(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    following_users = UserFollow.objects.filter(follower=profile_user).select_related(
        "followed"
    )

    context = {"profile_user": profile_user, "following_users": following_users}
    return render(request, "user_following.html", context)


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user).order_by(
        "-created_at"
    )
    return render(request, "notifications.html", {"notifications": user_notifications})


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.read = True
    notification.save()
    return redirect("notifications")



class UpdateCommentView(View):
    """
    View class to update a comment.
    """

    def dispatch(self, request, *args, **kwargs):
        # Override dispatch to apply login_required decorator to all HTTP methods
        return login_required(super().dispatch)(request, *args, **kwargs)

    def get(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
            comment_form = CommentForm(instance=comment)
            return render(request, "update_comment.html", {"comment_form": comment_form})
        except Comment.DoesNotExist:
            logger.error(f"Comment with ID {comment_id} does not exist for user {request.user}.")
            return redirect("home")  # Redirect to home page if comment does not exist
        except Exception as e:
            logger.error(f"Error retrieving comment (ID: {comment_id}): {e}")
            return redirect("home")  # Redirect to home page for other errors

    def post(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment_form.save()
                return redirect("recipe_detail", pk=comment.recipe.pk)
            # If form is not valid, render the form template again with errors
            return render(request, "update_comment.html", {"comment_form": comment_form})
        except Comment.DoesNotExist:
            logger.error(f"Comment with ID {comment_id} does not exist for user {request.user}.")
            return redirect("home")  # Redirect to home page if comment does not exist
        except Exception as e:
            logger.error(f"Error updating comment (ID: {comment_id}): {e}")
            return redirect("home")  # Redirect to home page for other errors


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == "POST":
        recipe_pk = comment.recipe.pk
        comment.delete()
        return redirect("recipe_detail", pk=recipe_pk)
    return render(request, "delete_comment.html", {"comment": comment})


@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    comments = recipe.comments.all()
    ratings = recipe.ratings.all()

    # Calculate average rating
    average_rating = (
        ratings.aggregate(Avg("score"))["score__avg"]
        if ratings.exists()
        else "No ratings yet"
    )

    # Check if the user has already rated this recipe
    user_rating = ratings.filter(author=request.user).first()

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        rating_form = RatingForm(request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.recipe = recipe
            new_comment.save()

            # Notify the recipe author
            send_notification.delay(
                recipient_id=recipe.author.id,
                # sender_id=request.user.id,
                message=f"{request.user.username} commented on your recipe {recipe.title}",
            )

            return redirect("recipe_detail", pk=recipe.pk)

        if rating_form.is_valid():
            if user_rating:
                # Update existing rating
                user_rating.score = rating_form.cleaned_data["score"]
                user_rating.save()
                messages.success(request, "Rating updated successfully.")
            else:
                # Create new rating
                new_rating = rating_form.save(commit=False)
                new_rating.author = request.user
                new_rating.recipe = recipe
                new_rating.save()

                # Notify the recipe author
                send_notification.delay(
                    recipient_id=recipe.author.id,
                    # sender_id=request.user.id,
                    message=f"{request.user.username} rated on your recipe {recipe.title}",
                )

            return redirect("recipe_detail", pk=recipe.pk)
    else:
        comment_form = CommentForm()
        rating_form = RatingForm()

    # Render template with recipe details, comments, and comment form
    return render(
        request,
        "recipe_detail.html",
        {
            "recipe": recipe,
            "comments": comments,
            "comment_form": comment_form,
            "ratings": ratings,
            "average_rating": average_rating,
            "rating_form": rating_form,
            "author_profile": recipe.author.profile,  # Pass author's profile
        },
    )


@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, pk=rating_id, author=request.user)
    if request.method == "POST":
        recipe_pk = rating.recipe.pk
        rating.delete()
        # messages.success(request, 'Rating deleted successfully.')
        return redirect("recipe_detail", pk=recipe_pk)
    return render(request, "your_app/delete_rating.html", {"rating": rating})


@login_required
def add_collection(request):
    if request.method == "POST":
        form = RecipeCollectionFormWithName(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            return redirect("collection_list")
    else:
        form = RecipeCollectionFormWithName()
    return render(request, "add_collection.html", {"form": form})


@login_required
def collection_list(request):
    collections = RecipeCollection.objects.filter(user=request.user)
    return render(request, "collection_list.html", {"collections": collections})



@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(RecipeCollection, id=collection_id)

    if request.method == "POST":
        form = RecipeCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, "Recipes added to collection successfully.")
            return redirect("collection_detail", collection_id=collection.id)
    else:
        form = RecipeCollectionForm(instance=collection)

    context = {
        "collection": collection,
        "form": form,
    }
    return render(request, "collection_detail.html", context)


# views.py

from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings


def send_test_email(request):
    send_mail(
        "Test Email",
        "This is a test email sent from Django.",
        settings.DEFAULT_FROM_EMAIL,  # Use the default from email configured in settings
        ["mail2mohanta99@gmail.com"],  # List of recipient email addresses
        fail_silently=False,
    )
    return render(
        request, "email_sent.html"
    )  # Render a template after sending the email


@staff_member_required
def popular_recipes(request):
    recipes = Recipe.objects.annotate(save_count=Count("collections")).order_by(
        "-save_count"
    )[:10]
    return render(request, "admin/popular_recipes.html", {"recipes": recipes})


@staff_member_required
def user_activity(request):
    users = User.objects.annotate(collection_count=Count("collections")).order_by(
        "-collection_count"
    )[:10]
    return render(request, "admin/user_activity.html", {"users": users})
