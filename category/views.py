


from django.shortcuts import render, redirect
from .models import Category, Product,SubCategory

def dashboardview(request):
    username = request.session.get('username')

    if not username:
        return redirect('login')

    categories = Category.objects.all()
    products = Product.objects.all()

    return render(request, "dashboard.html", {
        "username": username,
        "categories": categories,
        "products": products
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