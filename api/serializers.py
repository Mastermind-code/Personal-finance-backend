from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Category,Budget, Transaction


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", ]

class CategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Category
        fields = ['id', 'name', "user"]
        validators = [
            UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields = ['name', 'user'],
                message="you already have a category with the same name."
            )
        ]


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Budget
        fields = ['id', 'category', 'user', 'period', 'amount']
        validators = [
            UniqueTogetherValidator(
                queryset = Budget.objects.all(),
                fields = ['user', 'category'],
                message = 'You already have a budget for this category.'
            )
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'type', 'description', 'date']

    def validate_category(self, category):
        request = self.context.get("request")
        if category.user != request.user:
            raise serializers.ValidationError(
                "You cannot create a transaction under this category"
            )
        return category

