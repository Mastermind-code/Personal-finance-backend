from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_category_name_per_user')
        ]

    def __str__(self):
            return self.name


class Budget(models.Model):
    PERIOD_CHOICES = [
        ("monthly", "Monthly"),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=100, choices=PERIOD_CHOICES, default="monthly")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'category'], name="unique_budget_per_category_per_user")
        ]

    def __str__(self):
        return f"{self.user} - {self.category} -{self.amount} -"