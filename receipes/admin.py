 # Ensure you have imported 'admin_site' where needed in your project


from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from receipes.models import Profile, Recipe, RecipeCollection, Comment, Rating, UserFollow

class ProfileInline(admin.StackedInline):  #vertically layout within the admin form  
    model = Profile

class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]  #the relative model 'Profile' should have editable inline within the admin
    list_display = (
        'username', 'email',
        'recipe_count', 'follower_count', 'following_count',
        'comment_count', 'rating_count', 'recipe_comment_count', 'recipe_rating_count'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

    def recipe_count(self, obj):
        return obj.recipe_set.count()  #count of recipes associate with a user
    recipe_count.short_description = 'Recipes'  #column name inside User -->> Recipes

    def follower_count(self, obj):
        count = obj.followers.count()  #that calculates the number of followers for each user (obj).
        url = reverse('admin:user_followers', args=[obj.id])  
        return format_html('<a href="{}">{}</a>', url, count) #Generates a clickable link (<a> tag) that directs to a specific admin URL (admin:user_followers) showing the list of followers for that user.
    follower_count.short_description = 'Followers' #column name inside User

    def following_count(self, obj):
        count = obj.following.count()
        url = reverse('admin:user_following', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    following_count.short_description = 'Following'

    def comment_count(self, obj):
        count = obj.comment_set.count()
        url = reverse('admin:user_comments', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    comment_count.short_description = 'Comments'

    def rating_count(self, obj):
        count = obj.rating_set.count()
        url = reverse('admin:user_ratings', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    rating_count.short_description = 'Ratings'

    def recipe_comment_count(self, obj):
        count = Comment.objects.filter(recipe__author=obj).count()
        url = reverse('admin:user_recipe_comments', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    recipe_comment_count.short_description = 'Recipe Comments'

    def recipe_rating_count(self, obj):
        count = Rating.objects.filter(recipe__author=obj).count()
        url = reverse('admin:user_recipe_ratings', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    recipe_rating_count.short_description = 'Recipe Ratings'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/followers/', self.admin_site.admin_view(self.followers_view), name='user_followers'),
            path('<int:user_id>/following/', self.admin_site.admin_view(self.following_view), name='user_following'),
            path('<int:user_id>/comments/', self.admin_site.admin_view(self.comments_view), name='user_comments'),
            path('<int:user_id>/ratings/', self.admin_site.admin_view(self.ratings_view), name='user_ratings'),
            path('<int:user_id>/recipe_comments/', self.admin_site.admin_view(self.recipe_comments_view), name='user_recipe_comments'),
            path('<int:user_id>/recipe_ratings/', self.admin_site.admin_view(self.recipe_ratings_view), name='user_recipe_ratings'),
        ]
        return custom_urls + urls

    def followers_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        followers = UserFollow.objects.filter(followed=user).select_related('follower')
        context = dict(
            self.admin_site.each_context(request), # Adding common admin site context variables
            user=user,
            title='Followers',
            followers=followers,
        )
        return render(request, 'admin/user_followers.html', context)

    def following_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        following = UserFollow.objects.filter(follower=user).select_related('followed')
        context = dict(
            self.admin_site.each_context(request),
            user=user,
            title='Following',
            following=following,
        )
        return render(request, 'admin/user_following.html', context)

    def comments_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        comments = user.comment_set.all()  #a user will have multiple comments 
        context = dict(
            self.admin_site.each_context(request),
            user=user,
            title='Comments',
            comments=comments,
        )
        return render(request, 'admin/user_comments.html', context)

    def ratings_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        ratings = user.rating_set.all()
        context = dict(
            self.admin_site.each_context(request),
            user=user,
            title='Ratings',
            ratings=ratings,
        )
        return render(request, 'admin/user_ratings.html', context)

    def recipe_comments_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        comments = Comment.objects.filter(recipe__author=user).select_related('recipe')
        context = dict(
            self.admin_site.each_context(request),
            user=user,
            title='Recipe Comments',
            comments=comments,
        )
        return render(request, 'admin/user_recipe_comments.html', context)

    def recipe_ratings_view(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        ratings = Rating.objects.filter(recipe__author=user).select_related('recipe')
        context = dict(
            self.admin_site.each_context(request),
            user=user,
            title='Recipe Ratings',
            ratings=ratings,
        )
        return render(request, 'admin/user_recipe_ratings.html', context)

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'comment_count', 'rating_count')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at', 'updated_at')

    def comment_count(self, obj):
        count = obj.comments.count()
        url = reverse('admin:recipe_comments', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    comment_count.short_description = 'Comments'

    def rating_count(self, obj):
        count = obj.ratings.count()
        url = reverse('admin:recipe_ratings', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, count)
    rating_count.short_description = 'Ratings'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:recipe_id>/comments/', self.admin_site.admin_view(self.comments_view), name='recipe_comments'),
            path('<int:recipe_id>/ratings/', self.admin_site.admin_view(self.ratings_view), name='recipe_ratings'),
        ]
        return custom_urls + urls

    def comments_view(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        comments = recipe.comments.all()
        context = dict(
            self.admin_site.each_context(request),
            recipe=recipe,
            title='Comments',
            comments=comments,
        )
        return render(request, 'admin/recipe_comments.html', context)

    def ratings_view(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        ratings = recipe.ratings.all()
        context = dict(
            self.admin_site.each_context(request),
            recipe=recipe,
            title='Ratings',
            ratings=ratings,
        )
        return render(request, 'admin/recipe_ratings.html', context)

class RecipeCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'recipes_count', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at',)

    def recipes_count(self, obj):
        return obj.recipes.count()
    recipes_count.short_description = 'Recipes Count'

@method_decorator(staff_member_required, name='dispatch')
class PopularRecipesView(View):
    def get(self, request):
        recipes = Recipe.objects.annotate(save_count=Count('collections')).order_by('-save_count')[:10]
        return render(request, 'admin/popular_recipes.html', {'recipes': recipes})

@method_decorator(staff_member_required, name='dispatch')
class UserActivityView(View):
    def get(self, request):
        users = User.objects.annotate(recipe_count=Count('collections')).order_by('-recipe_count')[:10]
        return render(request, 'admin/user_activity.html', {'users': users})

class MyAdminSite(admin.AdminSite):
    site_header = 'My Admin Site'
    index_template = 'admin/index.html'  # Ensure this template exists

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('popular_recipes/', self.admin_view(PopularRecipesView.as_view()), name='popular_recipes'),
            path('user_activity/', self.admin_view(UserActivityView.as_view()), name='user_activity'),
        ]
        return custom_urls + urls

# Create an instance of MyAdminSite
admin_site = MyAdminSite(name='myadmin')

# Unregister User and Group from the default admin site if they are registered
try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Register User, Group, Recipe, and RecipeCollection with the custom admin site
admin_site.register(User, UserAdmin)
admin_site.register(Group)
admin_site.register(Recipe, RecipeAdmin)
admin_site.register(RecipeCollection, RecipeCollectionAdmin)
