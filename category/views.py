from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import (
    Category,
    SubCategory,
    Product,
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
    Order,
    OrderItem
)

@login_required
def dashboardview(request):

    # USER INFO
    username = request.user.username


    # CATEGORIES WITH SUBCATEGORIES
    categories = Category.objects.prefetch_related("subcategories").all()


    # WISHLIST
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    wishlist_product_ids = list(
        wishlist.items.values_list("product_id", flat=True)
    )

    wishlist_count = wishlist.items.count()


    # ================= FINAL SEARCH LOGIC =================

    query = request.GET.get('q', '').strip()

    if query:

        # 1️PRODUCT EXACT MATCH → OPEN PRODUCT DETAIL
        product = Product.objects.filter(
            name__iexact=query
        ).first()

        if product:
            return redirect('product_detail', product_id=product.id)


        # 2 SUBCATEGORY MATCH → SHOW PRODUCTS
        subcategory = SubCategory.objects.filter(
            name__icontains=query
        ).first()

        if subcategory:
            return redirect(
                'subcategory',
                subcategory_id=subcategory.id
            )


        # 3 CATEGORY MATCH → SHOW SUBCATEGORIES
        category = Category.objects.filter(
            name__icontains=query
        ).first()

        if category:
            return redirect(
                'category',
                category_id=category.id
            )


        # 4️ PARTIAL PRODUCT SEARCH → SHOW RESULTS PAGE
        products = Product.objects.filter(
            name__icontains=query
        )

        if products.exists():

            return render(request, "products.html", {
                "products": products,
                "title": f"Search Results for '{query}'",
                "username": username,
                "wishlist_count": wishlist_count
            })


    # RECENTLY VIEWED 

    recent_ids = request.session.get('recently_viewed', [])

    recently_viewed_queryset = Product.objects.filter(
        id__in=recent_ids
    )

    recently_viewed = sorted(
        recently_viewed_queryset,
        key=lambda x: recent_ids.index(x.id)
    )


    # RECOMMENDED 

    recommended = Product.objects.exclude(
        id__in=recent_ids
    ).order_by('?')[:4]


    #  JUST ARRIVED

    just_arrived = Product.objects.order_by('-id')[:8]


    # FINAL RENDER 

    context = {

        "username": username,

        "categories": categories,

        "recently_viewed": recently_viewed,

        "recommended": recommended,

        "just_arrived": just_arrived,

        "wishlist_product_ids": wishlist_product_ids,

        "wishlist_count": wishlist_count

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

    return render(request, "products.html", {
        "subcategory": subcategory,
        "products": products,
        "title": subcategory.name
    })
    
@login_required
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # Get recent list
    recent = request.session.get('recently_viewed', [])

    # Remove if already exists
    if product_id in recent:
        recent.remove(product_id)

    # Add to beginning
    recent.insert(0, product_id)

    # Keep only last 5 unique
    request.session['recently_viewed'] = recent[:5]

    # wishlist check
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    in_wishlist = WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).exists()

    return render(request, "product_detail.html", {
        "product": product,
        "in_wishlist": in_wishlist
    })

# @login_required
# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     # Recently viwed
#     recent = request.session.get('recently_viewed', [])

#     if product.id in recent:
#         recent.remove(product.id)

#     recent.insert(0, product.id)
#     request.session['recently_viewed'] = recent[:5]

#     # wishlist check
#     wishlist, created = Wishlist.objects.get_or_create(user=request.user)

#     in_wishlist = WishlistItem.objects.filter(
#         wishlist=wishlist,
#         product=product
#     ).exists()

#     return render(request, "product_detail.html", {
#         "product": product,
#         "in_wishlist": in_wishlist
#     })
    
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    cart = Cart.objects.get_or_create(user=request.user)[0]

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)

    return redirect('cart')

from .utils import apply_first_order_discount
@login_required
def cart_view(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in items)

    final_total, discount, _ = apply_first_order_discount(request.user, total)

    return render(request, "cart.html", {
        "items": items,
        "total": total,
        "discount": discount,
        "final_total": final_total
    })
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = Cart.objects.get_or_create(user=request.user)[0]
    cart.items.all().delete()

    CartItem.objects.create(cart=cart, product=product, quantity=1)

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')


from .utils import apply_first_order_discount

@login_required
def place_order(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = cart.items.all()

    if not items:
        return redirect('cart')

    total = sum(item.product.price * item.quantity for item in items)

    final_total, discount, discount_applied = apply_first_order_discount(
        request.user, total
    )

    order = Order.objects.create(   
        user=request.user,
        total_amount=final_total,
         discount_amount=discount   
    )
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart.items.all().delete()
    return redirect('my_orders')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "my_orders.html", {
        "orders": orders
    })
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

from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, ReturnRequest
from django.utils import timezone
from datetime import timedelta

def return_request(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 🔥 7-day policy
    if order.created_at < timezone.now() - timedelta(days=7):
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
  