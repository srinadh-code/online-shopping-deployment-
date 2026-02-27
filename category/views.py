
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from .models import Category, SubCategory, Product,Review
# from .models import Cart, CartItem,Wishlist,WishlistItem
# from django.shortcuts import redirect
from django.db.models import Min, Max,Avg


# @login_required
# def dashboardview(request):

#     username = request.user.username
#     categories = Category.objects.all()

#     # WISHLIST FIX
   
#     wishlist, created = Wishlist.objects.get_or_create(user=request.user)

#     wishlist_product_ids = list(
#         wishlist.items.values_list("product_id", flat=True)
#     )

#     wishlist_count = wishlist.items.count()
  

#     query = request.GET.get('q', '').strip()

#     # SEARCH SECTION
#     if query:

#         category = Category.objects.filter(name__icontains=query).first()
#         if category:
#             subcategories = SubCategory.objects.filter(category=category)
#             return render(request, "category.html", {
#                 "category": category,
#                 "subcategories": subcategories,
#                 "username": username,
#                 "wishlist_count": wishlist_count
#             })

#         subcategory = SubCategory.objects.filter(name__icontains=query).first()
#         if subcategory:
#             products = Product.objects.filter(subcategory=subcategory)
#             return render(request, "products.html", {
#                 "subcategory": subcategory,
#                 "products": products,
#                 "username": username,
#                 "wishlist_count": wishlist_count
#             })

#         products = Product.objects.filter(name__icontains=query)
        

#         return render(request, "products.html", {
#             "products": products,
#             "subcategory": None,
#             "username": username,
#             "wishlist_count": wishlist_count
#         })

#     # Recently Viewed
#     recent_ids = request.session.get('recently_viewed', [])
#     recently_viewed = Product.objects.filter(id__in=recent_ids)

#     recently_viewed = sorted(
#         recently_viewed,
#         key=lambda x: recent_ids.index(x.id)
#     )

#     recommended = Product.objects.all().order_by('?')[:4]
#     # Just Arrived (latest 6 products)
#     just_arrived = Product.objects.order_by('-id')[:8]

#     return render(request, "dashboard.html", {
#         "username": username,
#         "categories": categories,
#         "recently_viewed": recently_viewed,
#         "recommended": recommended,
#         "wishlist_product_ids": wishlist_product_ids,
#         "wishlist_count": wishlist_count,
#         "just_arrived": just_arrived
#     })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Category, SubCategory, Product
from .models import Cart, CartItem,Wishlist,WishlistItem
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

    # 🔹 Sorting
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

    #review submit 

    

    if request.method == "POST":
        print(request.POST)
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
        return redirect('product_detail', product_id=product.id)

    reviews = product.reviews.all().order_by("-created_at")
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    return render(request, "product_detail.html", {
        "product": product,
        "in_wishlist": in_wishlist,
        "reviews":reviews,
        "avg_rating":avg_rating
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
@login_required
def cart_view(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = cart.items.all()
    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
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

@login_required
def place_order(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = cart.items.all()

    if not items:
        return redirect('cart')

    total = sum(item.product.price * item.quantity for item in items)

    # Create Order
    order = Order.objects.create(
        user=request.user,
        total_amount=total
    )

    # Create OrderItems
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # Clear cart
    cart.items.all().delete()

    return redirect('my_orders')
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

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
