from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.hashers import make_password
from QuicklyCart_app.models import Product,Category,Seller,User,Rider
from django.contrib.sessions.models import Session
# Create your views here.


def index(request):
    product = list(Product.objects.values())
    category=list(Category.objects.values())
    return render(request,"index.html",{"product":product,"category":category})

def seller_page(request):
    user_id = request.session.get("user_id")
    seller = Seller.objects.get(user_id=user_id)
    products_qs = Product.objects.filter(seller_id=seller.seller_id)
    product = list(products_qs.values())
    category=list(Category.objects.values())

    # --- Seller dashboard stats ---
    # Items in stock: total number of distinct products
    items_in_stock = products_qs.count()

    # Orders related to this seller's products
    from QuicklyCart_app.models import Order
    seller_orders = Order.objects.filter(Product__in=products_qs)

    # New orders: pending or preparing
    new_orders = seller_orders.filter(status__in=["pending", "preparing"]).count()

    # Total sales: sum of price for delivered orders (price stored as string)
    def to_float_safe(val):
        try:
            return float(val)
        except Exception:
            return 0.0
    total_sales = 0.0
    for o in seller_orders.filter(status__in=["delivered", "shipped"]).only("price"):
        total_sales += to_float_safe(o.price)

    seller_stats = {
        "total_sales": int(total_sales) if total_sales.is_integer() else total_sales,
        "new_orders": new_orders,
        "items_in_stock": items_in_stock,
    }

    # Build orders list for this seller
    orders_data = []
    for o in seller_orders.select_related('user_id', 'Product').order_by('-created'):
        user = o.user_id
        product_obj = o.Product
        # Normalize status to UI-friendly lowercase values
        raw_status = (o.status or '').lower()
        status_map = {
            'placed': 'pending',
            'processing': 'preparing',
        }
        status = status_map.get(raw_status, raw_status or 'pending')
        orders_data.append({
            'id': f"QC{o.order_id}",
            'raw_id': o.order_id,
            'customer': f"{user.first_name} {user.last_name}" if user else '—',
            'items': f"{product_obj.name} x{o.quantity}",
            'status': status,
            'date': o.created.strftime('%Y-%m-%d'),
            'address': f"{user.address}, {user.city} - {user.pincode}" if user else '',
            'phone': user.mobile if user else '',
            'total': o.price,
        })

    import json as _json
    return render(request,"seller.html",{"product":product,"category":category, "seller_stats": seller_stats, "seller_orders": _json.dumps(orders_data)})

def delivery_page(request):
    user = None
    rider = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(user_id=user_id)
            rider = Rider.objects.filter(user_id=user).first()
        except User.DoesNotExist:
            user = None
            rider = None
    return render(request,"delivery.html", { 'user': user, 'rider': rider })

def rider_rules_page(request):
    user_id = request.session.get('user_id')
    rider = None
    status = None
    is_verified = False
    
    if user_id:
        try:
            user = User.objects.get(user_id=user_id)
            rider = Rider.objects.filter(user_id=user).first()
            status = (rider.status if rider else None)
            is_verified = user.is_verified
        except User.DoesNotExist:
            rider = None
            status = None
            is_verified = False
    
    return render(request, "rider_rules.html", { 
        'rider': rider, 
        'status': status, 
        'is_verified': is_verified 
    })

def product_page(request):
    return render(request,"product.html")

def admin_page(request):
    category=list(Category.objects.values())
    users = User.objects.filter(role='user').order_by('-created_at')
    sellers = Seller.objects.select_related('user_id').order_by('-created')
    
    # Calculate dashboard statistics
    total_users = User.objects.filter(role='user').count()
    total_sellers = Seller.objects.count()
    pending_sellers = Seller.objects.filter(status='Pending').count()
    
    # For riders, we'll use users with role='rider' if they exist, otherwise 0
    # Riders list from Rider model with related user
    riders = Rider.objects.select_related('user_id').order_by('-created')
    total_riders = riders.count()
    online_riders = riders.filter(status='Approved').count()
    
    # Calculate total revenue from orders (if any exist)
    from django.db.models import Sum
    from QuicklyCart_app.models import Order
    total_revenue = Order.objects.aggregate(
        total=Sum('price')
    )['total'] or 0
    
    # Active orders count
    active_orders = Order.objects.filter(status__in=['pending', 'processing', 'shipped']).count()
    
    dashboard_stats = {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'pending_sellers': pending_sellers,
        'total_riders': total_riders,
        'online_riders': online_riders,
        'total_revenue': total_revenue,
        'active_orders': active_orders,
        'riders': riders,
    }
    
    return render(request,"admin.html",{
        "category":category, 
        "users":users, 
        "sellers":sellers,
        "stats": dashboard_stats
    })

   # return render(request,"admin.html")

def seller_home(request):
    return render(request,"seller_home.html")

def rider_home(request):
    if request.method == 'POST':
        # Basic fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        password = make_password(request.POST.get('password'))
        gender = request.POST.get('gender', 'other')

        # Files
        profile_img = request.FILES.get('profileImage')
        id_proof_file = request.FILES.get('id_proof_file')
        dl_file = request.FILES.get('dl_file')
        rc_book = request.FILES.get('rc_book')

        # Save files via existing imagesaver in QuicklyCart_app.views through a proxy here
        from QuicklyCart_app.views import imagesaver, send_otp_email
        saved_profile = imagesaver(profile_img) if profile_img else ''
        saved_id = imagesaver(id_proof_file) if id_proof_file else ''
        saved_dl = imagesaver(dl_file) if dl_file else ''
        saved_rc = imagesaver(rc_book) if rc_book else ''

        # Create user with role rider, but unverified until OTP
        user = User(first_name=first_name, last_name=last_name, email=email, mobile=mobile,
                    address=address, city=city, pincode=pincode, gender=gender,
                    password=password, role='rider', image=saved_profile)
        user.save()

        docs = [
            {'id_proof_type': request.POST.get('id_proof_type', '')},
            {'id_proof_file': saved_id},
            {'dl_file': saved_dl},
            {'rc_book_file': saved_rc},
        ]
        Rider.objects.create(user_id=user, documents=docs, status='Pending')

        # Email OTP to verify email
        otp = send_otp_email(email)
        request.session['otp'] = otp
        request.session['otp_form'] = email
        request.session['pending_rider_user_id'] = user.user_id
        from django.contrib import messages
        messages.success(request, "Rider registration started. Please verify your email to continue.")
        # Redirect to OTP verification page
        from django.shortcuts import redirect
        return redirect('/rider/verify-otp/')
    # If already logged in as rider, prefill info
    initial = None
    user_id = request.session.get('user_id')
    if user_id:
        try:
            u = User.objects.get(user_id=user_id)
            if u.role == 'rider':
                initial = u
        except User.DoesNotExist:
            pass
    return render(request, "rider_home.html", { 'initial': initial })
