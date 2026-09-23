from django.contrib import admin
from QuicklyCart_app.models import User,Seller,Warehouse,Order,Product,Addtocart,Category,Rider


# Register your models here.
admin.site.register(User)
admin.site.register(Seller)
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Addtocart)
admin.site.register(Category)
admin.site.register(Rider)
