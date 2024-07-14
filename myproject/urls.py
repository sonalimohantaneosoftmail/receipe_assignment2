"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from receipes.admin import admin_site
# from receipes.admin import PopularRecipesView,UserActivityView
from django.urls import path
from receipes.views import recipe_detail,add_collection,collection_detail,collection_list,send_test_email,follow_user,unfollow_user,user_profile,notifications,mark_notification_as_read,user_activity,popular_recipes,add_recipe_to_collection,delete_collection,delete_recipe_from_collection,delete_comment,delete_rating,user_following
from receipes.views import RegisterView,HomeView,LogoutView,CreateRecipeView,LoginView,UpdateRecipeView,DeleteRecipeView,UserRecipesView
from receipes.views import ProfileUpdateView,ProfileDetailView
from receipes.views import UpdateCommentView


urlpatterns = [
    
    path('admin/',admin_site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/edit', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/', ProfileDetailView.as_view(), name='profile_view'),
    path('',HomeView.as_view(),name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('recipe/new/', CreateRecipeView.as_view(), name='create_recipe'),
    path('update_recipe/<int:pk>/', UpdateRecipeView.as_view(), name='update_recipe'),
    path('delete_recipe/<int:pk>/', DeleteRecipeView.as_view(), name='delete_recipe'),
    path('recipe_detail/<int:pk>/', recipe_detail, name='recipe_detail'),
    path('user_recipes/', UserRecipesView.as_view(), name='user_recipes'),

    path('update_comment/<int:comment_id>/', UpdateCommentView.as_view(), name='update_comment'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('delete_rating/<int:rating_id>/', delete_rating, name='delete_rating'),

    path('collections/add/', add_collection, name='add_collection'),
    path('collections/', collection_list, name='collection_list'),
    path('collections/<int:collection_id>/', collection_detail, name='collection_detail'),
    path('add_recipe_to_collection/<int:recipe_id>/', add_recipe_to_collection, name='add_recipe_to_collection'),
    path('delete_recipe_from_collection/<int:collection_id>/<int:recipe_id>/', delete_recipe_from_collection, name='delete_recipe_from_collection'),
    path('delete_collection/<int:collection_id>/', delete_collection, name='delete_collection'),

    path('send-email/', send_test_email, name='send_test_email'),

    path('follow/<int:user_id>/', follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow_user'),
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
    path('user/<int:user_id>/following/', user_following, name='user_following'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),

    path('admin/popular_recipes/',popular_recipes, name='popular_recipes'),
    path('admin/user_activity/', user_activity, name='user_activity'),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)