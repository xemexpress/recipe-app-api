"""
Tests for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_an_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'user@example.com'
        password = 'testpass123'

        user = create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            # normalized_email = get_user_model().objects.normalize_email(email)
            user = create_user(email, 'testpass123')

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without an email raises a ValueError."""
        test_cases = ['', '     ', 'a']
        for email in test_cases:
            with self.assertRaises(ValueError):
                user = get_user_model().objects.create_user(email, 'testpass123')

    def test_create_super_user(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe"""
        user = create_user(
            'test@example.com',
            'testpass123',
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample Recipe Name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag."""
        user = create_user()
        tag = models.Tag.objects.create(name='Tag1', user=user)

        self.assertEqual(str(tag), tag.name)
