from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, SubCategory, Product
#  dashboard search
def dashboardview(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')
    categories = Category.objects.all()
    query = request.GET.get('q')
    if query:
 #  Category Search
        category = Category.objects.filter(
            name__icontains=query
        ).first()

        if category:
            subcategories = SubCategory.objects.filter(category=category)
            return render(request, "category.html", {
                "username": username,
                "category": category,
                "subcategories": subcategories
            })

 # SubCategory Search
        subcategory = SubCategory.objects.filter(
            name__icontains=query
        ).first()

        if subcategory:
            products = Product.objects.filter(subcategory=subcategory)
            return render(request, "products.html", {
                "username": username,
                "subcategory": subcategory,
                "products": products,
                "title": subcategory.name
            })

 #  Product Search
        products = Product.objects.filter(
            name__icontains=query
        )

        return render(request, "products.html", {
            "username": username,
            "products": products,
            "title": "Search Results"
        })

 # dashboard normal
    # recently viewed  
    recent_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recent_ids)
        # maintain order
    recently_viewed = sorted(
        recently_viewed,
        key=lambda x: recent_ids.index(x.id)
    )

    # Recommended
    recommended = Product.objects.all().order_by('?')[:4]

    return render(request, "dashboard.html", {
        "username": username,
        "categories": categories,
        "recently_viewed": recently_viewed,
        "recommended": recommended
    })


# category page
def category_view(request, category_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    category = get_object_or_404(Category, id=category_id)
    subcategories = SubCategory.objects.filter(category=category)

    return render(request, "category.html", {
        "username": username,
        "category": category,
        "subcategories": subcategories
    })


# subcategory page
def subcategory_view(request, subcategory_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)

    return render(request, "products.html", {
        "username": username,
        "subcategory": subcategory,
        "products": products,
        "title": subcategory.name
    })


#  PRODUCT DETAIL PAGE 
def product_detail(request, product_id):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    # Recently viewed logic
    recent = request.session.get('recently_viewed', [])

    if product.id in recent:
        recent.remove(product.id)

    recent.insert(0, product.id)
    request.session['recently_viewed'] = recent[:5]

    return render(request, "product_detail.html", {
        "username": username,
        "product": product
    })