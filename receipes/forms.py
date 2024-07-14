# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe,Comment,Rating,Profile,RecipeCollection

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields=['title','ingredients','instructions','category','cooking_time','image']

class CommentForm(forms.ModelForm):
    class Meta:
        model =Comment
        fields = ['text']

class RatingForm(forms.ModelForm):
    class Meta:
        model=Rating
        fields=['score']

class RecipeCollectionForm(forms.ModelForm):
    class Meta:
        model = RecipeCollection
        fields = ['name','recipes']
        widgets = {
            'recipes': forms.CheckboxSelectMultiple,
        }


class RecipeCollectionFormWithName(forms.ModelForm):
    class Meta:
        model = RecipeCollection
        fields = ['name']
        


# class AddRecipeToCollectionForm(forms.Form):
#     recipe = forms.ModelChoiceField(queryset=Recipe.objects.all())

# users/forms.py
from django import forms
from .models import RecipeCollection, Recipe

class AddRecipeToCollectionForm(forms.ModelForm):
    collection = forms.ModelChoiceField(queryset=RecipeCollection.objects.none())

    class Meta:
        model = Recipe
        fields = ['collection']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AddRecipeToCollectionForm, self).__init__(*args, **kwargs)
        self.fields['collection'].queryset = RecipeCollection.objects.filter(user=user)

class DeleteRecipeFromCollectionForm(forms.Form):
    recipe_id = forms.IntegerField(widget=forms.HiddenInput)

class DeleteCollectionForm(forms.Form):
    collection_id = forms.IntegerField(widget=forms.HiddenInput)