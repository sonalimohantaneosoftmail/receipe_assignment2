from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm

User = get_user_model()

class RegisterViewTests(TestCase):

    def test_get_register_view(self):
        """
        Test the GET request for the registration view.
        """
        response = self.client.get(reverse('register'))  # Assuming the URL name is 'register'
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    # def test_post_register_view_valid(self):
    #     """
    #     Test the POST request with valid form data.
    #     """
    #     form_data = {
    #         'username': 'testuser',
    #         'password1': 'testpassword123',
    #         'password2': 'testpassword123',
    #     }
    #     response = self.client.post(reverse('register'), data=form_data)
    #     if response.status_code != 302:
    #         print(response.context['form'].errors)  # Print form errors if status is not redirect
    
    #         self.assertRedirects(response, '/home/')
    #         user = User.objects.get(username='testuser')
    #         self.assertIsNotNone(user)
    #         self.assertTrue(user.check_password('testpassword123'))
    #         self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_post_register_view_invalid(self):
        """
        Test the POST request with invalid form data.
        """
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'differentpassword',
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        self.assertContains(response, "The two password fields didn’t match.")
