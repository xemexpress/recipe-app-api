"""Serializers for recipe APIs"""

from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe list view."""

    class Meta:
        model = Recipe
        """Formulate a preview verision for the listing."""
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

    # def create(self, validated_data):
    #     """Create and return a new recipe"""
    #     return Recipe.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     """Update and return an existing recipe"""
    #     # instance.title = validated_data.get('title', instance.title)
    #     # instance.time_minutes = validated_data.get(
    #     #     'time_minutes', instance.time_minutes
    #     # )
    #     # instance.price = validated_data.get('price', instance.price)
    #     # instance.description = validated_data.get('description', instance.description)
    #     # instance.link = validated_data.get('link', instance.link)
    #     # instance.save()
    #     super().update(instance, validated_data)
    #     return instance


# class RecipeDetailSerializer(serializers.ModelSerializer):
#     """Serializer for recipe detail view."""
#     class Meta:
#         model = Recipe
#         """Formulate a detailed version for the recipe."""
#         fields = ('id', 'user', 'title', 'time_minutes', 'price', 'description', 'link')
#         read_only_fields = ('id', 'user')


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        """Formulate a detailed version for the recipe."""

        fields = RecipeSerializer.Meta.fields + ['description']
