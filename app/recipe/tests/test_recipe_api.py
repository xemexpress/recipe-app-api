"""Tests for Recipe APIs."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create(**params)


class PublicRecipeAPITests(TestCase):
    """Test public features of the recipe API."""

    def setUp(self):
        self.client = APIClient()

    # def test_retrieve_all_recipes(self):
    # """Test retrieving all recipes without credentials."""
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_recipe_without_credentials_error(self):
        """Test an error is returned when posting a recipe without credentials."""
        payload = {
            'titile': 'Sample Recipe Name',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test private features of the recipe API."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes."""
        create_recipe(self.user)
        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipes_limited_to_user(self):
        """Test a recipe list limited to authenticated user."""

        other_user = create_user(
            email='other@example.com',
            password='testpass',
            name='Test Name',
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_create_recipe_success(self):
    #     """Test creating a recipe."""
    #     recipe = Recipe(
    #         user=user,
    #         title='Sample Recipe Name',
    #         time_minutes=5,
    #         price=Decimal('5.50'),
    #         description='Sample recipe description',
    #     )
    # res =

    def test_retrieve_recipe_not_exists(self):
        """Test retrieving a recipe that does not exist."""
        url = detail_url(1)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe(self):
        """Test create recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
            # print(getattr(recipe, key), value)
            # print(type(getattr(recipe, key)), type(value))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'Original link'
        recipe = create_recipe(
            user=self.user,
            title='Original Title',
            link=original_link,
        )

        payload = {
            'title': 'New Recipe Title',
        }
        res = self.client.patch(detail_url(recipe_id=recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Recipe Title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {
            'title': 'New Recipe Title',
            'link': 'https://example.com/recipe.pdf',
            'description': 'New recipe description.',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # self.assertEqual(recipe.title, payload['title'])
        # self.assertEqual(recipe.link, payload['link'])
        # self.assertEqual(recipe.description, payload['description'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), payload[key])
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        recipe = create_recipe(
            user=self.user,
            title='Recipe Title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.',
        )
        other_user = create_user(
            email='other@example.com',
            password='testpass123',
        )

        url = detail_url(recipe.id)
        payload = {
            'user': other_user.id,
        }

        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test delete a recipe."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user's recipe gives error."""
        other_user = create_user(email='other@example.com', password='testpass123')
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
