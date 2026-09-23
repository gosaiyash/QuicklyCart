from django.db import models


# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    mobile = models.CharField(max_length=15)
    gender = models.CharField(max_length=7)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    pincode = models.CharField(max_length=12)
    password = models.CharField(max_length=355)
    role = models.CharField(max_length=10)
    image = models.CharField(max_length=450)
    is_verified = models.BooleanField(default = '0')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.last_name} {self.first_name}" 
    
class Seller(models.Model):
    seller_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User , on_delete = models.CASCADE)
    name = models.CharField(max_length=155)
    documents = models.JSONField()
    status = models.CharField(default='Pending')
    delivery_range = models.FloatField(default=5)
    gst_no = models.CharField(max_length=55)
    other_no = models.JSONField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    # Admin verification metadata
    verification = models.JSONField(null=True, blank=True)  # { filenameOrKey: "Approved"|"Rejected" }
    reject_reason = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    seller_id = models.ForeignKey(Seller , on_delete = models.CASCADE)
    name = models.CharField(max_length=155)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=155)
    pincode = models.CharField(max_length=10)
    capacity = models.CharField(max_length=255)
    documents = models.JSONField()
    status = models.CharField(default='Pending')
    created = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller_id = models.ForeignKey(Seller , on_delete = models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=20)
    description = models.TextField(max_length=1255)
    quantity = models.CharField(max_length=155)
    discount = models.CharField(max_length=155)
    images = models.JSONField()
    category = models.CharField(max_length=255)
    sub_category = models.CharField(max_length=255)
    #more_information = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User , on_delete= models.CASCADE)
    Product = models.ForeignKey(Product , on_delete = models.CASCADE)
    quantity = models.CharField(max_length=155)
    price = models.CharField(max_length=99)
    status = models.CharField(max_length=155)
    discount = models.CharField(max_length=155)
    payment_type = models.CharField(max_length=555)
    created = models.DateTimeField(auto_now_add=True)

class Addtocart(models.Model):
    addtocart_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User , on_delete= models.CASCADE)
    Product = models.ForeignKey(Product , on_delete = models.CASCADE)
    quantity = models.CharField(max_length=155)
    created = models.DateTimeField(auto_now_add=True)

class Rider(models.Model):
    rider_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    documents = models.JSONField()  # [{'id_proof_type': 'Aadhaar', 'id_proof_file': '...'}, {'dl_file': '...'}, {'rc_book_file': '...'}]
    status = models.CharField(default='Pending')
    created = models.DateTimeField(auto_now_add=True)
    km_away = models.CharField(default=3)
    verification = models.JSONField(null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    image = models.CharField(max_length=450)
    created = models.DateTimeField(auto_now_add=True)


# Rider delivery history: accept/complete/reject actions for orders
class RiderOrder(models.Model):
    ro_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='rider_events')
    rider = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='rider_account')
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_account')
    status = models.CharField(max_length=40)  # accepted / completed / rejected / picked_up / delivered
    pickup_address = models.CharField(max_length=255, blank=True, default='')
    delivery_address = models.CharField(max_length=255, blank=True, default='')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RiderOrder(ro_id={self.ro_id}, order=QC{self.order.order_id}, status={self.status})"










