from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory, Product
from .models import Cart, CartItem,Wishlist,WishlistItem,  Order, OrderItem
from django.shortcuts import redirect




@login_required
def dashboardview(request):

 
    # USER INFO
   
    username = request.user.username


    # CATEGORIES WITH SUBCATEGORIES
  
    categories = Category.objects.prefetch_related(
        "subcategories"
    ).all()


    # WISHLIST INFO
 
    wishlist, _ = Wishlist.objects.get_or_create(
        user=request.user
    )

    wishlist_product_ids = list(
        wishlist.items.values_list(
            "product_id",
            flat=True
        )
    )

    wishlist_count = wishlist.items.count()


    # SEARCH FUNCTIONALITY

    query = request.GET.get("q", "").strip()

    if query:

        products = Product.objects.filter(
            name__icontains=query
        ).only(
            "id", "name", "price", "image"
        )[:50]

        return render(
            request,
            "products.html",
            {
                "products": products,
                "username": username,
                "wishlist_count": wishlist_count,
                "wishlist_product_ids": wishlist_product_ids
            }
        )



    # JUST ARRIVED
    # Send more products for auto rotation

    just_arrived = list(
        Product.objects
        .only("id", "name", "price", "image")
        .order_by("-id")[:12]
    )



    # RECENTLY VIEWED
    # STATIC — changes only when user opens product

    recent_ids = request.session.get(
        "recently_viewed",
        []
    )[:12]

    recently_viewed_queryset = Product.objects.filter(
        id__in=recent_ids
    ).only(
        "id", "name", "price", "image"
    )

    recently_viewed = list(recently_viewed_queryset)

    # Preserve order based on session
    recently_viewed.sort(
        key=lambda x: recent_ids.index(x.id)
    )
    # RECOMMENDED
    # Send more products for rotation
   
    recommended = list(
        Product.objects
        .only("id", "name", "price", "image")
        .order_by("?")[:12]
    )
    # FINAL CONTEXT
   
    context = {

        "username": username,

        "categories": categories,

        "just_arrived": just_arrived,

        "recently_viewed": recently_viewed,

        "recommended": recommended,

        "wishlist_product_ids": wishlist_product_ids,

        "wishlist_count": wishlist_count,

    }


    return render(
        request,
        "dashboard.html",
        context
    )




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

    # Recently viewed
    recent = request.session.get('recently_viewed', [])

    if product.id in recent:
        recent.remove(product.id)

    recent.insert(0, product.id)
    request.session['recently_viewed'] = recent[:5]

    # Wishlist check
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    in_wishlist = WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).exists()

    return render(request, "product_detail.html", {
        "product": product,
        "in_wishlist": in_wishlist
    })
    
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
from .models import Order, OrderItem
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
from .models import Order

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, "my_orders.html", {
        "orders": orders
    })

from django.http import JsonResponse
@login_required
def wishlist_view(request):

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    items = wishlist.items.select_related("product")

    return render(request, "wishlist.html", {
        "items": items
    })


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
from django.http import HttpResponse
from .models import Order

def reset_orders(request):
    Order.objects.filter(user=request.user).delete()
    return HttpResponse("Orders Reset Done ")
def order_success(request):
    user = request.user

    # Count how many orders user has
    order_count = user.order_set.count()   # change 'order_set' if your model name is different

    # First order check
    is_first_order = order_count == 1

    return render(request, "order_success.html", {
        "is_first_order": is_first_order
    })