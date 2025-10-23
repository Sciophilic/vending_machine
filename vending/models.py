from django.db import models
from django.utils import timezone
import json

class Product(models.Model):
    PRODUCT_TYPES = [
        ('CAKE', '🎂 Cakes'),
        ('CHOCOLATE', '🍫 Chocolates'), 
        ('DRINK', '🥤 Soft Drinks'),
    ]
    
    product_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.IntegerField(default=0)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES)
    image = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.product_id} - {self.name}"
    
    @property  # Add this decorator to make it a property
    def is_available(self):
        return self.quantity > 0
    
    # Add this property to get image URL for templates
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class Transaction(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    total_amount_inserted = models.IntegerField(default=0)
    amount_required = models.IntegerField(default=0)
    change_returned = models.IntegerField(default=0)
    products_purchased = models.TextField(blank=True)
    
    def __str__(self):
        return f"Transaction at {self.timestamp}"
    
    def set_products_purchased(self, products_list):
        self.products_purchased = json.dumps(products_list)
    
    def get_products_purchased(self):
        return json.loads(self.products_purchased) if self.products_purchased else []

class DenominationLog(models.Model):
    DENOMINATIONS = [
        (500, 'Rs 500'),
        (200, 'Rs 200'),
        (100, 'Rs 100'),
        (50, 'Rs 50'),
        (20, 'Rs 20'),
        (10, 'Rs 10'),
        (5, 'Rs 5'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='denominations')
    denomination = models.IntegerField(choices=DENOMINATIONS)
    quantity_inserted = models.IntegerField(default=0)
    quantity_returned = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Rs {self.denomination} - Inserted: {self.quantity_inserted}, Returned: {self.quantity_returned}"