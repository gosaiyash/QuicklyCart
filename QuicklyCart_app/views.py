from django.shortcuts import render,redirect,get_object_or_404
from datetime import datetime
from QuicklyCart_app.models import User ,Seller,Product,Category,Addtocart,Order,Rider
from django.contrib.auth.hashers import make_password ,check_password 
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.core.mail import send_mail
import random
from django.contrib.sessions.models import Session
from django.http import JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from django.conf import settings
# Create your views here.


def user_register(request):
    
    if request.method == 'POST':
       first_name = request.POST.get('firstName') 
       last_name = request.POST.get('lastName')
       email = request.POST.get('email')
       mobile = request.POST.get('phone')
       address = request.POST.get('address1')
       pincode = request.POST.get('pincode')
       city = request.POST.get('city')
       gender = request.POST.get('gender')
       password = make_password(request.POST.get('password'))
       image = request.FILES['profileImage']

       if User.objects.filter(email=email).first():
            user = User.objects.filter(email=email).first()
            if user.is_verified == True:
                messages.error(request , "Email already exist ! ")
                return redirect('/')
            else:
                User.objects.filter(email=email).delete()

       if request.FILES['profileImage']:
           #image move to static/images
           image_name = datetime.now().strftime('%Y%m%d%H%M%S')
           extension_parts = image.name.split('.')
           newname = image_name + '.' + extension_parts[-1]
           file = FileSystemStorage(location='static/images')
           file.save(newname,image)
           userobj = User(first_name=first_name,last_name=last_name,email=email,mobile=mobile,address=address,
                      pincode=pincode,city=city,gender=gender,password=password,role='user',image=newname,created_at=datetime.today())
           userobj.save()
       else:
            userobj = User(first_name=first_name,last_name=last_name,email=email,mobile=mobile,address=address,
                      pincode=pincode,city=city,gender=gender,password=password,role='user',image=None,created_at=datetime.today())
            userobj.save()

       request.session['otp_form']=email

       #otp ,email send
       otp = send_otp_email(email)
       request.session['otp'] =otp
       
    return redirect('/')


def user_login(request):
    if request.method == 'POST':
        
        email = request.POST.get('username', '').strip()
        users_qs = User.objects.filter(email=email).order_by('-created_at')
        if not users_qs.exists():
            messages.error(request, "User not found!")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        user = users_qs.first()

        if user:
            if check_password(request.POST['password'],user.password):
                request.session['user_name'] = user.first_name + user.last_name
                request.session['user_id'] = user.user_id
                request.session['image'] = user.image
                messages.success(request, "Login successful !")
                if user.role == 'user':
                    return redirect('/')
                elif user.role == 'seller':
                    return redirect('/seller')
                elif user.role == 'rider':
                    rider = Rider.objects.filter(user_id=user).first()
                    if rider and str(rider.status).lower() == 'approved':
                        return redirect('/delivery')
                    else:
                        messages.info(request, "Your rider account is awaiting admin approval.")
                        return redirect('/rider/rules/')
                
            else:
                messages.error(request, "Password does not match ! Login Fail ! ")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        else:
            messages.error(request, "User not found ! Login fail  !")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        

def send_otp_email(email):
    otp = random.randint(111111, 999999)  
    
    subject = 'QuicklyCart Verification'
    message = f'Your OTP is {otp} for verification. It is valid for 5 minutes.'
    from_email = 'gosaiyash13@gmail.com'
    
    send_mail(subject, message, from_email, [email])
    
    return otp
   

def logout_user(request):
    Session.objects.all().delete()
    list(messages.get_messages(request))
    return redirect('/')

i=0

def verify_otp(request):
    user_otp = request.POST["otp"]
    otp = request.session.get("otp")
    email=request.session.get("otp_form")
    global i
    if int(user_otp) == otp:
        User.objects.filter(email=email).update(is_verified = True)
        del request.session['otp_form']
        del request.session['otp']   
        messages.success(request, "User Register Successfully !")     
        return redirect('/')
    else:
        if i==3:
            user = User.objects.filter(email=email).first()
            user.delete()
            Session.objects.all().delete()
            messages.error(request, "Wrong otp ! Limit Reach !")   
            return redirect('/')
        else:
            i+=1
            messages.error(request, "Wrong otp ! try again !")
            return redirect('/')
        
def resendotp(request):
    email=request.session.get("otp_form")
    otp = send_otp_email(email)
    request.session['otp'] = otp
    messages.success(request, "Otp Sended !")
    return redirect('/')

def verify_rider_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get("otp")
        email = request.session.get("otp_form")
        pending_user_id = request.session.get('pending_rider_user_id')
        
        global i
        if int(user_otp) == session_otp:
            # Verify the rider user
            User.objects.filter(user_id=pending_user_id).update(is_verified=True)
            
            # Set user session
            user = User.objects.get(user_id=pending_user_id)
            request.session['user_email'] = user.email
            request.session['user_id'] = user.user_id
            
            # Clean up OTP session data
            del request.session['otp_form']
            del request.session['otp']
            del request.session['pending_rider_user_id']
            
            messages.success(request, "Email verified successfully! Your rider application is now submitted for admin approval.")
            return redirect('/rider/rules/')
        else:
            if i == 3:
                # Delete the user if OTP attempts exceeded
                User.objects.filter(user_id=pending_user_id).delete()
                Session.objects.all().delete()
                messages.error(request, "Wrong OTP! Maximum attempts reached. Please register again.")
                return redirect('/becomeRider/')
            else:
                i += 1
                messages.error(request, f"Wrong OTP! {3-i} attempts remaining.")
                return redirect('/rider/verify-otp/')
    
    # Check if there's a pending OTP verification
    if not request.session.get('otp') or not request.session.get('otp_form'):
        messages.error(request, "No OTP verification session found. Please register again.")
        return redirect('/becomeRider/')
    
    return render(request, 'rider_otp_verification.html')

def resend_rider_otp(request):
    email = request.session.get("otp_form")
    if not email:
        messages.error(request, "No email found in session. Please register again.")
        return redirect('/becomeRider/')
    
    otp = send_otp_email(email)
    request.session['otp'] = otp
    messages.success(request, "OTP sent successfully!")
    return redirect('/rider/verify-otp/')

#seller 
def seller_register(request):
      
    if request.method == 'POST':
       first_name = request.POST.get('first_name') 
       last_name = request.POST.get('last_name')
       email = request.POST.get('email')
       mobile = request.POST.get('mobile')
       address = request.POST.get('address')
       pincode = request.POST.get('pincode')
       city = request.POST.get('city')
       gender = request.POST.get('gender')
       password = make_password(request.POST.get('password'))
       image = request.FILES['profileImage']

       if User.objects.filter(email=email).first():
            messages.error(request , "Email already exist ! ")
            return redirect('/')

       if request.FILES['profileImage']:
           #image move to static/images
           image_name = datetime.now().strftime('%Y%m%d%H%M%S')
           extension_parts = image.name.split('.')
           newname = image_name + '.' + extension_parts[-1]
           file = FileSystemStorage(location='static/images')
           file.save(newname,image)
           userobj = User(first_name=first_name,last_name=last_name,email=email,mobile=mobile,address=address,
                      pincode=pincode,city=city,gender=gender,password=password,role='seller',image=newname,created_at=datetime.today())
           userobj.save()
       else:
            userobj = User(first_name=first_name,last_name=last_name,email=email,mobile=mobile,address=address,
                      pincode=pincode,city=city,gender=gender,password=password,role='seller',image=None,created_at=datetime.today())
            userobj.save()


       request.session['otp_form']=email

        #otp ,email send
       otp = send_otp_email(email)
       request.session['otp'] =otp
       
    return redirect('/becomeSeller')

def verify_seller_otp(request):
    if request.method == 'POST':
      
      user_otp = request.POST['userotp']
      otp = request.session.get("otp")
      email=request.session.get("otp_form")
      global i
      if int(user_otp) == otp:
         user = User.objects.filter(email=email).first() 
         request.session['user_email'] = user.email
         request.session['user_id'] = user.user_id
         del request.session['otp_form']
         del request.session['otp']  
         User.objects.filter(email=email).update(is_verified = "1")
         messages.success(request, "User Basic information saved ! Please Verify Documents !")     
         return redirect('/becomeSeller')
      else:
         if i==3:
             user = User.objects.filter(email=email).first()
             user.delete()
             Session.objects.all().delete()
             messages.error(request, f"Wrong otp !{i} Limit Reach  !")   
             return redirect('/becomeSeller')
         else:
             i+=1
             messages.error(request, "Wrong otp ! try again !")
             return redirect('/becomeSeller')
    return redirect('/becomeSeller')

def seller_doc_save(request):
    if request.method == "POST":
        id_proof_file =request.FILES['id_proof_file']
        address_proof_file =request.FILES['address_proof_file']
        id_proof_file =imagesaver(id_proof_file)
        address_proof_file =imagesaver(address_proof_file)
        doc= [{'idProofType':id_proof_file} ,
               {'address_proof_type':address_proof_file}
             ],
        user_id = request.session.get('user_id')
        user = User.objects.get(user_id = user_id)
        
        seller = Seller(
        user_id = user ,
        name = "temp",
        documents = doc,     
        gst_no = request.POST['gst_no']

        )
        seller.save()
        messages.success(request, "Documnets successfully sended for verification !")
        del request.session['user_email']
        del request.session['user_id']
        return redirect('/becomeSeller')
  
def imagesaver(image):
     image_name = datetime.now().strftime('%Y%m%d%H%M%S%f')
     extension_parts = image.name.split('.')
     newname = image_name + '.' + extension_parts[-1]
     file = FileSystemStorage(location='static/images')
     file.save(newname,image)
     return newname


#product add

def addproduct(request):
    if request.method == 'POST':
        product_name = request.POST.get('productName')
        product_price = request.POST.get('productPrice')
        product_stock = request.POST.get('productStock')
        main_category_id = request.POST.get('productMainCategory')
        sub_category_id = request.POST.get('productSubCategory', '')  # default empty string
        description = request.POST.get('productDescription')
        images = request.FILES.getlist('productImages')
        imageslist = []
        for img in images:
            newimage = imagesaver(img)
            imageslist.append(newimage)
            
        user_id = request.session.get("user_id")
        seller = Seller.objects.get(user_id = user_id)
        # Map category IDs to names for consistent filtering across site
        main_category_name = ''
        sub_category_name = ''
        try:
            if main_category_id:
                main_category_name = Category.objects.get(id=main_category_id).name
        except Category.DoesNotExist:
            main_category_name = ''
        try:
            if sub_category_id:
                sub_category_name = Category.objects.get(id=sub_category_id).name
        except Category.DoesNotExist:
            sub_category_name = ''
        product = Product(
            seller_id = seller,
            name = product_name,
            price = product_price,
            description = description,
            quantity = product_stock,
            discount = 0,
            category = main_category_name,
            sub_category = sub_category_name,
            images = imageslist
        )

        product.save()
        messages.success(request , "Product added successfully !")
        return redirect('/seller')


def get_product(request):
    
   product = list(Product.objects.values())

   return JsonResponse(product,safe=False)

def forgot_password(request):
    email = request.POST['email_forgot']

    if User.objects.filter(email=email):
        otp = send_otp_email(email)
        request.session['forgot_password_otp'] = otp
        request.session['forgot_password_email'] = email
        messages.success(request, "Otp sended to ur mail !")
    else:
        messages.error(request, "User not found  !")

    return redirect('/')

def verify_forgot_password_otp(request):
    userotp=request.POST['otp']
    otp = request.session.get('forgot_password_otp')

    if int(userotp) == otp:
        del request.session['forgot_password_otp']
        request.session['user_new_password'] = 1
        messages.success(request, "Set ur new password!")
    else:
        messages.error(request, "Wrong otp !")

    return redirect('/')

def newpassword(request):
    password = request.POST['new_password']
    email = request.session.get('forgot_password_email')
    hashpassword = make_password(password)

    user = User.objects.filter(email = email ).update(password = hashpassword)

    if user:
        del request.session['forgot_password_email']
        del request.session['user_new_password']
        messages.success(request, "Password successfully updated !")
    else:
        messages.error(request, "Something is wrong !")
    return redirect('/')

def moreinforproduct(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    # Related products from same main category
    related = list(
        Product.objects.filter(category=product.category)
        .exclude(product_id=product.product_id)
        .values()
    )[:8]
    return render(request , 'product.html' , {"product":product, "related": related})

def product_update(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('productName')
        product_price = request.POST.get('productPrice')
        product_stock = request.POST.get('productStock')
        main_category = request.POST.get('productMainCategory')
        sub_category = request.POST.get('productSubCategory')
        description = request.POST.get('productDescription')
        discount = request.FILES.getlist('productdiscount')
        images = request.FILES.getlist('productImages')
        imageslist = []
        for img in images:
            newimage = imagesaver(img)
            imageslist.append(newimage)

        is_updated = Product.objects.filter(product_id=product_id).update(
            name = product_name,
            price = product_price,
            description = description,
            quantity = product_stock,
            discount = discount,
            category = main_category,
            sub_category = sub_category,
            images = imageslist
        )

        if is_updated:
            messages.success(request , "Product Updated successfully !")
        else:
            messages.success(request , "Error in Product Updated ! Try again later !")
  
    return redirect('/seller')

def DeleteProduct(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.delete()
    messages.success(request , "Product is Deleted Successfully !")
    return redirect('/seller')

# ---------------- CART API (Add/Update/Remove) ---------------- #

def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        return {}

def _current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None

def cart_add(request):
    data = _json_body(request)
    user = _current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    if not product_id:
        return JsonResponse({'ok': False, 'error': 'product_id_required'}, status=400)
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'product_not_found'}, status=404)
    item, created = Addtocart.objects.get_or_create(user_id=user, Product=product, defaults={'quantity': '0'})
    new_qty = int(item.quantity or 0) + max(quantity, 1)
    item.quantity = str(new_qty)
    item.save()
    return JsonResponse({'ok': True, 'quantity': new_qty})

def cart_update(request):
    data = _json_body(request)
    user = _current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 0))
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'product_not_found'}, status=404)
    try:
        item = Addtocart.objects.get(user_id=user, Product=product)
    except Addtocart.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not_found'}, status=404)
    if quantity <= 0:
        item.delete()
        return JsonResponse({'ok': True, 'removed': True})
    item.quantity = str(quantity)
    item.save()
    return JsonResponse({'ok': True, 'quantity': quantity})


def cart_remove(request):
    data = _json_body(request)
    user = _current_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
    product_id = data.get('product_id')
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'ok': True})
    Addtocart.objects.filter(user_id=user, Product=product).delete()
    return JsonResponse({'ok': True})

# def add_category(request):
#     if request.method == "POST":
#         category_type = request.POST.get("type")   
#         parent_id = request.POST.get("parent")     
#         name = request.POST.get("name")           
#         image = request.FILES.get("image") 

#         newimage = imagesaver(image) 
#         parent = get_object_or_404(Category, id=parent_id)
#         Category.objects.create(name=name, parent=parent, image=newimage)
#         messages.success(request , "Categoy is added !")
#         referer = request.META.get('HTTP_REFERER')
#         return HttpResponseRedirect(referer)

def add_category(request):
    if request.method == "POST":
        # Common form fields
        category_id = request.POST.get("edit_id", "").strip()
        name = request.POST.get("name", "").strip()
        category_type = request.POST.get("type", "main").strip()
        parent_id = request.POST.get("parent", "").strip()
        image_file = request.FILES.get("image")

        # Resolve parent when sub-category
        parent = None
        if category_type == "sub" and parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                parent = None

        # Save image if provided and keep only its saved filename in DB
        saved_image_name = None
        if image_file:
            saved_image_name = imagesaver(image_file)

        # EDIT existing category
        if category_id:
            try:
                category_obj = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                messages.error(request, "Category not found")
                return redirect(request.META.get("HTTP_REFERER", "/admin/"))

            category_obj.name = name or category_obj.name
            # For main types, ensure parent is None
            category_obj.parent = None if category_type == "main" else parent
            if saved_image_name:
                category_obj.image = saved_image_name
            # If no new image uploaded, keep existing image
            category_obj.save()
            messages.success(request, "Category updated successfully!")
        else:
            # CREATE new category
            Category.objects.create(
                name=name,
                parent=parent if category_type == "sub" else None,
                image=saved_image_name or ""
            )
            messages.success(request, "Category added successfully!")

        return redirect(request.META.get("HTTP_REFERER", "/admin/"))

    return redirect("/admin/")

def profile(request):
    user_id = request.session.get("user_id")
    user = User.objects.filter(user_id=user_id).first()
    total_orders = Order.objects.filter(user_id_id=user_id).count() if user_id else 0
    addresses_count = 1 if (user and (user.address or user.city or user.pincode)) else 0
    return render(request , 'profile.html' , {"user":user, "total_orders": total_orders, "addresses_count": addresses_count}) 

def order_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to view orders')
        return redirect('/')
    orders = (Order.objects
              .filter(user_id_id=user_id)
              .select_related('Product')
              .order_by('-created'))
    return render(request, 'orders.html', { 'orders': orders })

def profile_update(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Please login to update profile')
        return redirect('/')
    user = User.objects.filter(user_id=user_id).first()
    if request.method == 'POST':
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        mobile = request.POST.get('mobile', user.mobile)
        address = request.POST.get('address', user.address)
        city = request.POST.get('city', user.city)
        pincode = request.POST.get('pincode', user.pincode)
        gender = request.POST.get('gender', user.gender)
        # Optional profile image upload
        img = request.FILES.get('image')
        if img:
            newname = imagesaver(img)
            user.image = newname
            request.session['image'] = newname
        user.first_name = first_name
        user.last_name = last_name
        user.mobile = mobile
        user.address = address
        user.city = city
        user.pincode = pincode
        user.gender = gender
        user.save()
        request.session['user_name'] = user.first_name + user.last_name
        messages.success(request, 'Profile updated successfully!')
        return redirect('/profile/')
    return redirect('/profile/')


# ---------------- SELLER: ORDER STATUS UPDATE API ---------------- #
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def seller_order_status_update(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'method_not_allowed'}, status=405)
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'ok': False, 'error': 'unauthenticated'}, status=401)
    try:
        seller = Seller.objects.get(user_id=user_id)
    except Seller.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not_seller'}, status=403)
    try:
        import json
        data = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        data = {}
    order_id = data.get('order_id')
    status = (data.get('status') or '').strip()
    if not order_id or not status:
        return JsonResponse({'ok': False, 'error': 'missing_params'}, status=400)
    try:
        order = Order.objects.select_related('Product').get(order_id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'order_not_found'}, status=404)
    # Ensure this order belongs to this seller
    if order.Product.seller_id.seller_id != seller.seller_id:
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    order.status = status
    order.save(update_fields=['status'])
    return JsonResponse({'ok': True, 'status': order.status})


def edit_product_view(request,product_id):
#    product = list(Product.objects.filter(product_id = product_id).values())
    product = get_object_or_404(Product, pk=product_id)

    context ={
        "update_product" : "True",
        "p" : product,
    }
    return render(request, "product_update.html" , context)

# def update_product_save(request,product_id):
#     if request.method == 'POST':
       
#         product_name = request.POST.get('productName')
#         product_price = request.POST.get('productPrice')
#         product_stock = request.POST.get('productStock')
#         main_category = request.POST.get('productMainCategory')
#         # sub_category = request.POST.get('productSubCategory')
#         description = request.POST.get('productDescription')
#         # discount = request.FILES.getlist('productdiscount')
#         images = request.FILES.getlist('productImages')
#         # This line reads the "image_A.jpg,image_B.jpg" string from the form
#         images_to_remove_str = request.POST.get('images_to_remove', '')
#         # This is the core logic in your views.py file

#         if images_to_remove_str:  # It's not empty
#             # 1. Turn the string into a list: ['image_A.jpg', 'image_B.jpg']
#             images_to_remove = images_to_remove_str.split(',')

#             # 2. Make a copy of the original image list to modify it
#             current_images = list(product.images) # ['image_A.jpg', 'image_B.jpg', 'image_C.jpg']

#             # 3. Loop through the images marked for removal
#             for image_path in images_to_remove:
#                 if image_path in current_images:
#                     # 4. Remove the image from the list and delete the file
#                     # ... (file deletion code) ...
#                     current_images.remove(image_path)

#             # 5. The list now only contains the images that were NOT removed
#             product.images = current_images # Becomes ['image_C.jpg']
#         imageslist = []
#         for img in images:
#             newimage = imagesaver(img)
#             imageslist.append(newimage)

#         Product.objects.filter(product_id=product_id).update(
#             name = product_name,
#             price = product_price,
#             description = description,
#             quantity = product_stock,
#             # discount = discount,
#             category = main_category,
#             # sub_category = sub_category,
#              images = imageslist
#         )

#         if True:
#             messages.success(request , "Product Updated successfully !")
#         else:
#             messages.success(request , "Error in Product Updated ! Try again later !")
  
#     return redirect('/seller')

def update_product_save(request, product_id):
    if request.method == 'POST':
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found!")
            return redirect('/seller')
        
        product.name = request.POST.get('productName')
        product.price = request.POST.get('productPrice')
        product.quantity = request.POST.get('productStock')
        product.category = request.POST.get('productMainCategory')
        product.description = request.POST.get('productDescription')

        images_to_remove_str = request.POST.get('images_to_remove', '')
        if images_to_remove_str:
            images_to_remove = images_to_remove_str.split(',')
            
            for image_path in images_to_remove:
                if image_path in product.images:
                    
                    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
                    if os.path.exists(full_path):
                        os.remove(full_path)
                   
                    product.images.remove(image_path)

       
        new_images = request.FILES.getlist('productImages')
        for img in new_images:
            new_image_path = imagesaver(img)
            product.images.append(new_image_path)

        try:
            product.save()
            messages.success(request, "Product updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating product: {e}")
 
    return redirect('/seller')



def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(user_id=user_id)
            user.delete()
            return JsonResponse({'success': True, 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def debug_categories(request):
    categories = Category.objects.all()
    debug_info = []
    for cat in categories:
        debug_info.append({
            'id': cat.id,
            'name': cat.name,
            'image_field': cat.image,
            'image_exists': os.path.exists(f'static/images/{cat.image}') if cat.image else False,
            'parent': cat.parent.name if cat.parent else None
        })
    return JsonResponse({'categories': debug_info})


def approve_seller(request, seller_id):
    if request.method == 'POST':
        try:
            seller = Seller.objects.get(seller_id=seller_id)
            seller.status = 'Approved'
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                payload = {}
            seller.verification = payload.get('verification') or seller.verification
            seller.reject_reason = ''
            from datetime import datetime as _dt
            seller.verified_at = _dt.now()
            seller.save()
            return JsonResponse({'success': True, 'message': 'Seller approved successfully'})
        except Seller.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Seller not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# def debug_categories(request):
#     categories = Category.objects.all()
#     debug_info = []
#     for cat in categories:
#         debug_info.append({
#             'id': cat.id,
#             'name': cat.name,
#             'image_field': cat.image,
#             'image_exists': os.path.exists(f'static/images/{cat.image}') if cat.image else False,
#             'parent': cat.parent.name if cat.parent else None
#         })
#     return JsonResponse({'categories': debug_info})

def reject_seller(request, seller_id):
    if request.method == 'POST':
        try:
            seller = Seller.objects.get(seller_id=seller_id)
            seller.status = 'Rejected'
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                payload = {}
            seller.reject_reason = payload.get('reason', '')
            seller.verification = payload.get('verification') or seller.verification
            from datetime import datetime as _dt
            seller.verified_at = _dt.now()
            seller.save()
            return JsonResponse({'success': True, 'message': 'Seller rejected successfully'})
        except Seller.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Seller not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Rider Admin Actions
def approve_rider(request, rider_id):
    if request.method == 'POST':
        try:
            rider = Rider.objects.get(rider_id=rider_id)
            rider.status = 'Approved'
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                payload = {}
            rider.verification = payload.get('verification') or rider.verification
            rider.reject_reason = ''
            from datetime import datetime as _dt
            rider.verified_at = _dt.now()
            rider.save()
            return JsonResponse({'success': True, 'message': 'Rider approved successfully'})
        except Rider.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Rider not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def reject_rider(request, rider_id):
    if request.method == 'POST':
        try:
            rider = Rider.objects.get(rider_id=rider_id)
            rider.status = 'Rejected'
            try:
                payload = json.loads(request.body.decode('utf-8') or '{}')
            except Exception:
                payload = {}
            rider.reject_reason = payload.get('reason', '')
            rider.verification = payload.get('verification') or rider.verification
            from datetime import datetime as _dt
            rider.verified_at = _dt.now()
            rider.save()
            return JsonResponse({'success': True, 'message': 'Rider rejected successfully'})
        except Rider.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Rider not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ---------------- BUY NOW FLOW ---------------- #

def _require_login(request):
    if not request.session.get('user_id'):
        messages.error(request, "Please login to continue")
        return False
    return True

def buynow_start(request, product_id):
    if not _require_login(request):
        return redirect('/')
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found")
        return redirect('/')
    request.session['buynow'] = {
        'product_id': product.product_id,
        'quantity': 1
    }
    return redirect('/checkout/address/')

def cart_checkout(request):
    if not _require_login(request):
        return redirect('/')
    
    user = User.objects.get(user_id=request.session.get('user_id'))
    cart_items = Addtocart.objects.filter(user_id=user)
    
    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect('/')
    
    # Mark this as a cart checkout and save the session
    request.session['cart_checkout'] = True
    request.session.save()
    
    # Redirect to address selection
    return redirect('/checkout/address/')

def checkout_address(request):
    if not _require_login(request):
        return redirect('/')
    user = User.objects.filter(user_id=request.session.get('user_id')).first()
    # For now, we treat the single address fields on User as the only saved address.
    addresses = [{
        'id': 1,
        'address': user.address,
        'city': user.city,
        'pincode': user.pincode
    }] if user else []
    return render(request, 'select_address.html', { 'addresses': addresses })

def checkout_payment(request):
    if not _require_login(request):
        return redirect('/')
    
    user = User.objects.get(user_id=request.session.get('user_id'))
    cart_items = []
    total_price = 0
    discounted_total = 0
    
    try:
        # Check if this is a cart checkout or buynow
        if request.session.get('cart_checkout'):
            # Get all cart items with product details
            cart_items = list(Addtocart.objects.select_related('Product').filter(user_id=user))
            
            # Calculate totals
            for item in cart_items:
                if item.Product:  # Make sure product exists
                    try:
                        price = float(item.Product.price)
                        quantity = int(item.quantity)
                        total_price += price * quantity
                        discounted_total += (price * 0.9) * quantity  # 10% discount
                    except (ValueError, TypeError) as e:
                        print(f"Error processing item {item.id}: {str(e)}")
                        continue
        else:
            # Handle buynow flow
            buynow = request.session.get('buynow') or {}
            if buynow.get('product_id'):
                try:
                    product = Product.objects.get(product_id=buynow['product_id'])
                    quantity = int(buynow.get('quantity', 1))
                    price = float(product.price)
                    total_price = price * quantity
                    discounted_total = (price * 0.9) * quantity  # 10% discount
                    cart_items = [{'Product': product, 'quantity': quantity}]
                except (Product.DoesNotExist, ValueError, TypeError) as e:
                    print(f"Error processing buynow item: {str(e)}")
                    messages.error(request, "Error processing product. Please try again.")
                    return redirect('/')
        
        # Print debug information
        print("Cart Items Count:", len(cart_items))
        print("Total Price:", total_price)
        print("Discounted Total:", discounted_total)
        
        return render(request, 'payment.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'discounted_total': discounted_total,
            'is_cart_checkout': bool(request.session.get('cart_checkout'))
        })
        
    except Exception as e:
        print(f"Error in checkout_payment: {str(e)}")
        messages.error(request, "An error occurred while processing your cart. Please try again.")
        return redirect('/')

def place_cod_order(request):
    if request.method != 'POST':
        return redirect('/checkout/payment/')
    if not _require_login(request):
        return redirect('/')
    buynow = request.session.get('buynow') or {}
    user = User.objects.get(user_id=request.session.get('user_id'))
    product = Product.objects.filter(product_id=buynow.get('product_id')).first()
    if not product:
        messages.error(request, "Product not found")
        return redirect('/')
    quantity = int(buynow.get('quantity', 1))
    # price after 10% discount like listing
    try:
        original_price = float(product.price)
    except Exception:
        original_price = 0.0
    price = original_price * 0.9
    
    # Create and save the order
    order = Order(
        user_id=user,
        Product=product,
        quantity=str(quantity),
        price=str(round(price * quantity, 2)),
        status='Placed',
        discount='10',
        payment_type='COD'
    )
    order.save()
    
    # clear buynow session
    if 'buynow' in request.session:
        del request.session['buynow']
    
    # Also clear cart if this was a cart checkout
    if 'cart_checkout' in request.session:
        # Remove items from cart after successful order
        Addtocart.objects.filter(user_id=user).delete()
        del request.session['cart_checkout']
        
    messages.success(request, "Order placed successfully!")
    return redirect('/')


# New: Place order for all items in cart (Cart Checkout)
def place_cart_order(request):
    if request.method != 'POST':
        return redirect('/checkout/payment/')
    if not _require_login(request):
        return redirect('/')
    user = User.objects.get(user_id=request.session.get('user_id'))
    # Ensure we are in cart checkout mode
    if not request.session.get('cart_checkout'):
        messages.error(request, 'No cart checkout in progress')
        return redirect('/')
    items = list(Addtocart.objects.select_related('Product').filter(user_id=user))
    if not items:
        messages.error(request, 'Your cart is empty')
        return redirect('/')
    created_count = 0
    for item in items:
        if not item.Product:
            continue
        try:
            original_price = float(item.Product.price)
        except Exception:
            original_price = 0.0
        discounted_unit = original_price * 0.9
        try:
            qty = int(item.quantity or 1)
        except Exception:
            qty = 1
        order = Order(
            user_id=user,
            Product=item.Product,
            quantity=str(qty),
            price=str(round(discounted_unit * qty, 2)),
            status='Placed',
            discount='10',
            payment_type='COD'
        )
        order.save()
        created_count += 1
    # Clear cart and session flag
    Addtocart.objects.filter(user_id=user).delete()
    if 'cart_checkout' in request.session:
        del request.session['cart_checkout']
    messages.success(request, f"Order placed successfully for {created_count} item(s)!")
    return redirect('/')

# def debug_categories(request):
#     categories = Category.objects.all()
#     debug_info = []
#     for cat in categories:
#         debug_info.append({
#             'id': cat.id,
#             'name': cat.name,
#             'image_field': cat.image,
#             'image_exists': os.path.exists(f'static/images/{cat.image}') if cat.image else False,
#             'parent': cat.parent.name if cat.parent else None
#         })
#     return JsonResponse({'categories': debug_info})
