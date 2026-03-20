from django.db.models import Avg, Min, Max,Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import ExtractMonth
from django.core.paginator import Paginator
from .models import Cart, CartItem, ProductVariant
from .utils import apply_first_order_discount
from  .models import RecentlyViewed
from .models import Profile
from django.contrib import messages
from .models import ReturnRequest
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table#invoice 
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet#invoice 
from .models import Address
from .forms import AddressForm
from django.http import JsonResponse
from .models import Product
from django.contrib.auth import authenticate, login
from django.db import transaction
from .models import (
    Category,
    SubCategory,
    Product,
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
    Order,
    OrderItem,
    Review
)


def dashboardview(request):

    #  user info 
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = "Guest"

    # categories
    categories = Category.objects.prefetch_related("subcategories").all()

    #  wishlist
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        wishlist_product_ids = list(
            wishlist.items.values_list("product_id", flat=True)
        )
        wishlist_count = wishlist.items.count()
    else:
        wishlist_product_ids = []
        wishlist_count = 0

    #  search functionality (UNCHANGED)
    query = request.GET.get('q', '').strip()
    if query:
        product = Product.objects.filter(name__iexact=query).first()
        if product:
            return redirect('product_detail', product_id=product.id)

        subcategory = SubCategory.objects.filter(name__icontains=query).first()
        if subcategory:
            return redirect('subcategory', subcategory_id=subcategory.id)

        category = Category.objects.filter(name__icontains=query).first()
        if category:
            return redirect('category', category_id=category.id)

        products = Product.objects.filter(name__icontains=query)
        if products.exists():
            return render(request, "products.html", {
                "products": products,
                "title": f"Search Results for '{query}'",
                "username": username,
                "wishlist_count": wishlist_count
            })

 
    recently_viewed = []

    if request.user.is_authenticated:
        recent_db = RecentlyViewed.objects.filter(
            user=request.user
        ).select_related('product')[:5]

        recently_viewed = [item.product for item in recent_db]

    if not recently_viewed:
        session_ids = request.session.get('recently_viewed', [])
        qs = Product.objects.filter(id__in=session_ids)

        recently_viewed = sorted(
            qs,
            key=lambda x: session_ids.index(x.id)
        )

        #recommeded
    recent_ids = [p.id for p in recently_viewed]

    #  recommended
    recommended = Product.objects.exclude(
        id__in=recent_ids
    ).order_by('?')[:4]

    #  trending
    trending_products = Product.objects.annotate(
        cart_count=Count('cartitem')
    ).order_by('-cart_count')[:4]

    most_purchased = Product.objects.annotate(
        total_orders=Count("orderitem")
    ).order_by("-total_orders")[:4]

    #  just arrived
    just_arrived = Product.objects.order_by('-id')[:8]

    #  cart safe
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()
    else:
        cart_count = 0

    # render
    context = {
        "username": username,
        "categories": categories,
        "recently_viewed": recently_viewed,
        "recommended": recommended,
        "just_arrived": just_arrived,
        "wishlist_product_ids": wishlist_product_ids,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "trending_products": trending_products,
        "most_purchased": most_purchased,
    }

    return render(request, "dashboard.html", context)

@login_required
def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = SubCategory.objects.filter(category=category)
    return render(request, "category.html", {
        "category": category,
        "subcategories": subcategories
    })
@login_required
def subcategory_view(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)

    price_data = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    min_price = price_data['min_price'] or 0
    max_price = price_data['max_price'] or 0

    if max_price > min_price:
        range_size = (max_price - min_price) // 3

        price_ranges = [
            (min_price, min_price + range_size),
            (min_price + range_size + 1, min_price + 2*range_size),
            (min_price + 2*range_size + 1, max_price)
        ]
    else:
        price_ranges = []

    price_range = request.GET.get("price_range")

    if price_range:
        min_p, max_p = price_range.split("-")
        products = products.filter(
            price__gte=int(min_p),
            price__lte=int(max_p)
        )

    #  Sorting
    sort = request.GET.get("sort")

    sort_map = {
        "price_low": "price",
        "price_high": "-price"
    }   

    sort_value = sort_map.get(sort, "-id")
    products = products.order_by(sort_value)

    return render(request, "products.html", {
        "subcategory": subcategory,
        "products": products,
        "title": subcategory.name,
        "price_ranges":price_ranges
    })

def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    print("OPENED PRODUCT ID:", product.id)

    # Variants
    variants = ProductVariant.objects.filter(product=product)

    #  recently viewed sessions 
    recent = request.session.get('recently_viewed', [])

    if product_id in recent:
        recent.remove(product_id)

    recent.insert(0, product_id)
    request.session['recently_viewed'] = recent[:5]

    # db recently viewd
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()}
        )

    # default
    in_wishlist = False
    can_review = False
    user_review = None

    # logged in
    if request.user.is_authenticated:

        # wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

        in_wishlist = WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product
        ).exists()

        # can review (only delivered) after delivery
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status="Delivered"
        ).exists()

        # existing review
        user_review = Review.objects.filter(
            product=product,
            user=request.user
        ).first()

    #submit review
    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect('login')  #  force login

        if not can_review:
            messages.error(request, "You can review only after delivery.")
            return redirect('product_detail', product_id=product.id)

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    "rating": int(rating),
                    "comment": comment
                }
            )

        return redirect('product_detail', product_id=product.id)

    # reviews
    reviews = product.reviews.all().order_by("-created_at")
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, "product_detail.html", {
        "product": product,
        "variants": variants,
        "in_wishlist": in_wishlist,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "can_review": can_review,
        "user_review": user_review
    })


@login_required
def add_to_cart(request, product_id):

    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))
    variant = ProductVariant.objects.get(id=variant_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        variant=variant,
        quantity=quantity,
        defaults={
            "quantity": 1,
            "price": variant.product.price
        }
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("cart")

@login_required
def cart_view(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.items.select_related("product")

    total = sum(
        item.price * item.quantity
        for item in items
    )

    final_total, discount, _ = apply_first_order_discount(
        request.user,
        total
    )

    return render(request, "cart.html", {
        "items": items,
        "total": total,
        "discount": discount,
        "final_total": final_total
    })

@login_required
def buy_now(request, product_id):

    variant_id = request.POST.get("variant_id")

    if not variant_id:
        messages.error(request, "Please select a size.")
        return redirect("product_detail", product_id=product_id)

    variant = ProductVariant.objects.get(id=variant_id)
    quantity = int(request.POST.get("quantity", 1))
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart.items.all().delete()

    CartItem.objects.create(
        cart=cart,
        product=variant.product,
        variant=variant,
        quantity=quantity,
        price=variant.product.price
    )

    return redirect("cart")

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')


@login_required
def place_order(request):

    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = cart.items.all()

    if not items:
        return redirect('cart')

    payment_method = request.POST.get("payment_method", "COD")

    
    request.session["payment_method"] = payment_method

    profile = Profile.objects.filter(user=request.user).first()

    if not profile or not profile.address or not profile.phone:
        messages.warning(request, "Please fill your profile details before placing the order.")
        return redirect('profile')


    total = sum(item.price * item.quantity for item in items)

    final_total, discount, is_first = apply_first_order_discount(
    request.user, total)
    coins_used = 0

    if request.POST.get("use_coins"):

        profile = request.user.profile

        coins_used = min(profile.coins, final_total)
        final_total = final_total - coins_used

        profile.coins -= coins_used
        profile.save()

    request.session["final_total"] = float(final_total)
    request.session["discount"] = float(discount)
    request.session["coins_used"] = coins_used
    request.session["is_first_order"] = is_first    

    
    return redirect("address")


@transaction.atomic
@login_required
def create_order(request):

    cart = Cart.objects.get(user=request.user)
    items = cart.items.select_related("variant", "product")
    coins_used = request.session.get("coins_used", 0)

    if not items:
        order = Order.objects.filter(user=request.user).last()
        if order:
            return redirect("order_success")
        return redirect("cart")

    payment_method = request.session.get("payment_method", "COD")
    final_total = request.session.get("final_total")
    discount = request.session.get("discount")
    if final_total is None:
        total = sum(item.price * item.quantity for item in items)
        final_total, discount, _ = apply_first_order_discount(request.user, total)

    order = Order.objects.create(
        user=request.user,
        total_amount=final_total,
        discount_amount=discount,
        coins_used=coins_used,
        payment_method=payment_method,
        payment_status="Pending" if payment_method == "COD" else "Paid"
    )

    
    order.save()

    for item in items:

        # LOCK VARIANT (NOT PRODUCT)
        variant = item.variant.__class__.objects.select_for_update().get(id=item.variant.id)

        # CORRECT VALIDATION
        if item.quantity > variant.stock:
            messages.error(
                request,
                f"{variant.attribute_value.value} only has {variant.stock} items available"
            )
            raise Exception("Stock issue")

        # CREATE ORDER ITEM
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=variant,
            quantity=item.quantity,
            price=item.price
        )

        #  CORRECT STOCK UPDATE
        variant.stock -= item.quantity
        variant.save()


    cart.items.all().delete()

#  CLEAR SESSION 
    request.session.pop("coins_used", None)
    request.session.pop("final_total", None)
    request.session.pop("discount", None)
    return redirect("order_success")

@login_required
def card_payment(request):
    amount = request.session.get("final_total", 0)

    if request.method == "POST":
        return redirect("payment_processing")

    return render(request,"card_payment.html",{"amount":amount})
@login_required
def upi_payment(request):
    amount = request.session.get("final_total", 0)
    if request.method == "POST":
        return redirect("payment_processing")
    return render(request,"upi_payment.html",{"amount":amount})

@login_required
def payment_processing(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()
    if not items:
        return redirect("cart")

    payment_method = request.session.get("payment_method", "COD")
    final_total = request.session.get("final_total")
    discount = request.session.get("discount")

    if final_total is None:
        total = sum(item.price * item.quantity for item in items)
        final_total, discount, _ = apply_first_order_discount(request.user, total)

    order = Order.objects.create(
        user=request.user,
        total_amount=final_total,
        discount_amount=discount,
        payment_method=payment_method,
        payment_status="Paid"
    )

    
    order.save()

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            price=item.price
        )

    cart.items.all().delete()

    return render(request,"payment_processing.html")


@login_required
def order_success(request):
    order = Order.objects.filter(user=request.user).last()
    return render(request,"order_success.html",{"order":order})





@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    now = timezone.now()

    for order in orders:

        if not order.created_at:
            continue

        diff = now - order.created_at

        
        if diff < timedelta(seconds=30):
            order.display_status = "Placed"

        
        elif diff < timedelta(minutes=1):
            order.display_status = "Shipped"

        
        else:
            order.display_status = "Delivered"

            
            if order.status != "Delivered":
                order.status = "Delivered"
                order.delivered_at = now
                order.save()

    return render(request, "my_orders.html", {"orders": orders})
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "Delivered":
        order.status = "Cancelled"
        order.save()

    return redirect("my_orders")

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )
    items = wishlist.items.select_related("product")

    return render(request, "wishlist.html", {
        "items": items
    })
from django.http import JsonResponse
@login_required
def toggle_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )
    wishlist_item = WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        status = "removed"
    else:
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product
        )
        status = "added"

    return JsonResponse({"status": status})
@login_required
def remove_from_wishlist(request, item_id):

    item = get_object_or_404(
        WishlistItem,
        id=item_id,
        wishlist__user=request.user
    )

    item.delete()
    return redirect("wishlist")

def reset_orders(request):
    Order.objects.filter(user=request.user).delete()
    return HttpResponse("Orders Reset Done ")
def order_success(request):
    user = request.user
    # Count how many orders user has
    order_count = user.order_set.count()   
    # First order check
    is_first_order = order_count == 1
    return render(request, "order_success.html", {
        "is_first_order": is_first_order
    })
from django.shortcuts import get_object_or_404, redirect

@login_required
def return_request(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    
    if order.status != "Delivered":
        return redirect("my_orders")


    if not order.delivered_at:
        return redirect("my_orders")


    if order.delivered_at < timezone.now() - timedelta(days=7):
        return redirect("my_orders")


    if ReturnRequest.objects.filter(order=order).exists():
        return redirect("my_orders")

    if request.method == "POST":

        request_type = request.POST.get("type")
        reason = request.POST.get("reason")
        image = request.FILES.get("image")

        ReturnRequest.objects.create(
            order=order,
            user=request.user,
            request_type=request_type,
            reason=reason,
            image=image
        )

        return redirect("my_orders")

    return render(request, "return_form.html", {"order": order})


def save_model(self, request, obj, form, change):

    if obj.status == "Approved":
        obj.refund_status = "Completed"

    super().save_model(request, obj, form, change)
def my_returns(request):
    returns = ReturnRequest.objects.filter(user=request.user)
    return render(request, "my_returns.html", {"returns": returns})   

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def increase_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.quantity += 1
    item.save()

    return redirect("cart")


@login_required
def decrease_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")




@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph(f"Invoice - Order #{order.id}", styles['Title']))
    elements.append(Spacer(1, 12))

    # User Info
    elements.append(Paragraph(f"Customer: {request.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Date: {order.created_at}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table Data
    data = [["Product", "Quantity", "Price"]]

    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"₹{item.price}"
        ])

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Total
    elements.append(Paragraph(f"Discount: ₹{order.discount_amount}", styles['Normal']))
    elements.append(Paragraph(f"Total Amount: ₹{order.total_amount}", styles['Heading2']))

    doc.build(elements)

    return response


@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")
        profile.city = request.POST.get("city")
        profile.state = request.POST.get("state")
        profile.pincode = request.POST.get("pincode")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        else:
            return render(request,"admindashboard/admin_login.html",{"error": " only admin can access"})

    return render(request,"admindashboard/admin_login.html")



@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect("dashboard")
    
    top_products = (
    OrderItem.objects
    .values('product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:5]
    )
    orders = Order.objects.all().order_by('-id')[:5]

    total_orders = Order.objects.count()

    delivered_orders = Order.objects.filter(status="Delivered").count()

    total_products = Product.objects.count()

    total_customers = User.objects.count()

    low_stock_products = Product.objects.filter(stock__lte=5)

    monthly_orders = (
        Order.objects
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    # ORDER STATUS
    pending = Order.objects.filter(status="Pending").count()
    delivered = Order.objects.filter(status="Delivered").count()
    cancelled = Order.objects.filter(status="Cancelled").count()

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "total_products": total_products,
        "total_customers": total_customers,
        "low_stock_products":low_stock_products,
         "monthly_orders": list(monthly_orders),
        "pending": pending,
        "delivered": delivered,
        "cancelled": cancelled,
        "top_products": top_products
    }

    return render(request, "admindashboard/dash.html", context)



def admin_products(request):

    if request.method == "POST":

        action = request.POST.get("action")
        if action == "add":

            name = request.POST.get("name")
            price = request.POST.get("price")
            stock = request.POST.get("stock")
            category_id = request.POST.get("category")
            subcategory_id = request.POST.get("subcategory")

            category = Category.objects.get(id=category_id)
            subcategory = SubCategory.objects.get(id=subcategory_id)

            image = request.FILES.get("image")

            Product.objects.create(
                name=name,
                price=price,
                stock=stock,
                category=category,
                subcategory=subcategory,
                image=image
            )

        # UPDATE PRODUCT
        elif action == "update":

            product_id = request.POST.get("product_id")
            price = request.POST.get("price")
            stock = request.POST.get("stock")

            product = Product.objects.get(id=product_id)
            product.price = price
            product.stock = stock
            product.save()

        return redirect("admin_products")
    # SEARCH
    query = request.GET.get("q")
    products = Product.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    if query:
        products = products.filter(name__icontains=query)
    # PAGINATION
    paginator = Paginator(products,9)

    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)


    return render(request, "admindashboard/products.html", {
        "products": products,
        "query": query,
        "categories":categories,
        "subcategories":subcategories

    })


def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")

        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        product.category_id = category_id
        product.subcategory_id = subcategory_id

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("admin_products")

    return render(request,"admindashboard/edit_product.html",{
        "product":product,
        "categories":categories,
        "subcategories":subcategories
    })
      
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    product.delete()

    return redirect("admin_products")

def admin_orders(request):

    orders = Order.objects.order_by("id")

    paginator = Paginator(orders,15)

    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)
    return render(request,"admindashboard/orders.html",{
        "orders":orders,
    
    })


from django.contrib.auth.models import User

def admin_customers(request):

    customers = User.objects.all()

    return render(request,"admindashboard/customer.html",{
        "customers":customers
    })


def admin_order_detail(request, order_id):

    order = Order.objects.get(id=order_id)

    if request.method == "POST":

        status = request.POST.get("status")

        order.status = status
        order.save()

    items = order.items.all()

    return render(request,"admindashboard/order_detail.html",{
        "order":order,
        "items":items
    })

def customer_orders(request, user_id):

    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user)

    return render(request,"admindashboard/customer_orders.html",{
        "customer":user,
        "orders":orders
    })
    
    

def find_similar(request, product_id):
    product = Product.objects.get(id=product_id)
    similar = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    data = []

    for p in similar:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image": p.image.url
        })

    return JsonResponse({"products": data})


def address_page(request):
    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)

            address.user = request.user   
            address.save()
            request.session["selected_address"] = address.id
            return redirect("place_order")

    else:
        form = AddressForm()
    addresses = Address.objects.filter(user=request.user)
    return render(request,"address.html",{
        "form":form,
        "addresses":addresses
    })

@login_required
def deliver_here(request, id):
    request.session["selected_address"] = id
    payment_method = request.session.get("payment_method")
    print("PAYMENT METHOD:", payment_method)
    if payment_method == "CARD":
        return redirect("card_payment")

    elif payment_method == "UPI":
        return redirect("upi_payment")

    elif payment_method == "COD":
        return redirect("create_order")

    return redirect("cart")

def order_placed(request):
    address_id = request.session.get("selected_address")
    address = None
    if address_id:
        address = Address.objects.get(id=address_id)

    return render(request,"order_placed.html",{
        "address":address
    })

def edit_address(request, id):
    address = get_object_or_404(Address, id=id)

    form = AddressForm(instance=address)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect("address")
    return render(request, "edit_address.html", {"form": form})


def delete_address(request, id):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return redirect("address")
