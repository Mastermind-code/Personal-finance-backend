from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from decimal import Decimal
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
    spent = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    remaining = serializers.SerializerMethodField()

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Budget
        fields = ['id', 'category', 'user', 'period', 'amount', 'spent', 'remaining']
        read_only_fields = ["spent", "remaining"]

        validators = [
            UniqueTogetherValidator(
                queryset = Budget.objects.all(),
                fields = ['user', 'category'],
                message = 'You already have a budget for this category.'
            )
        ]
    def get_remaining(self, obj):
        spent = getattr(obj, "spent", Decimal("0.00"))
        return obj.amount - spent


class TransactionSerializer(serializers.ModelSerializer):
    is_over_budget = serializers.SerializerMethodField()
    remaining_budget = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'type', 'description', 'date', 'is_over_budget', 'remaining_budget']
        read_only_fields = ["is_over_budget", "remaining_budget"]
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        transaction = Transaction.objects.create(**validated_data)

        budget_context = self.evaluate_budget(transaction)
        if budget_context:
            transaction._budget_context = budget_context

        return transaction

    def evaluate_budget(self, transaction):
        if transaction.type != 'expenditure':
            return None
        
        today = now().date()
        month_start = today.replace(day=1)

        budget = Budget.objects.filter(
            user = transaction.user,
            category = transaction.category,
            period = "month"
        ).first()

        if not budget:
            return None

        spent = (
            Transaction.objects.filter(
                user=transaction.user,
                category=transaction.category,
                type=transaction.EXPENDITURE,
                date__gte=month_start,
            ).aggregate(
                total_spent=Sum("amount")
            )['total_spent'] or Decimal("0.00")
        )

        remaining = budget.amount - spent

        

        return {
            "is_over_budget": remaining < 0,
            "remaining_budget": remaining,
        }

    def get_is_over_budget(self, obj):
        context = getattr(obj, "_budget_context", None)
        if context:
            return context["is_over_budget"]
        return False

    def get_remaining_budget(self, obj):
        context = getattr(obj, "_budget_context", None)
        if context:
            return context["remaining_budget"]
        return None

    def validate_category(self, category):
        request = self.context.get("request")
        if category.user != request.user:
            raise serializers.ValidationError(
                "You cannot create a transaction under this category"
            )
        return category

