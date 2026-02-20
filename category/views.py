

from django.shortcuts import render, redirect
from .models import Category, Product,SubCategory

# def dashboardview(request):
#     username = request.session.get('username')

#     if not username:
#         return redirect('login')

#     categories = Category.objects.all()
#     products = Product.objects.all()

#     return render(request, "dashboard.html", {
#         "username": username,
#         "categories": categories,
#         "products": products
#     })
    
def dashboardview(request):
    username = request.session.get('username')

    if not username:
        return redirect('login')

    categories = Category.objects.all()

    # Recently Viewed
    recent_ids = request.session.get('recently_viewed', [])
    recently_viewed = Product.objects.filter(id__in=recent_ids)

    # Maintain correct order
    recently_viewed = sorted(
        recently_viewed,
        key=lambda x: recent_ids.index(x.id)
    )

    #  Recommended (Random 4)
    recommended = Product.objects.all().order_by('?')[:4]

    return render(request, "dashboard.html", {
        "username": username,
        "categories": categories,
        "recently_viewed": recently_viewed,
        "recommended": recommended
    })
def category_view(request, id):
    category = Category.objects.get(id=id)
    subcategories = SubCategory.objects.filter(category=category)

    return render(request, "category.html", {
        "category": category,
        "subcategories": subcategories
    })
    
def subcategory_view(request, id):
    subcategory = SubCategory.objects.get(id=id)
    products = Product.objects.filter(subcategory=subcategory)

    return render(request, "products.html", {
        "products": products,
        "subcategory": subcategory
    })
    
    
    
    
def product_detail(request, id):
    product = Product.objects.get(id=id)

    # Get existing session list or empty list
    recent = request.session.get('recently_viewed', [])

    # Remove if already exists (to avoid duplicates)
    if id in recent:
        recent.remove(id)

    # Insert at beginning
    recent.insert(0, id)

    # Keep only last 5 products
    recent = recent[:5]

    # Save back to session
    request.session['recently_viewed'] = recent

    return render(request, "product_detail.html", {
        "product": product
    })