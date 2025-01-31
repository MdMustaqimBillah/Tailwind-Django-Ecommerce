from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Category, Product
from .forms import ProductForm
from Review.models import Review
from Carousel.models import Carousel
from django.core.paginator import Paginator
from django.views.generic import FormView, ListView, DetailView, DeleteView
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

def product_list(request, category_slug=None):
    category = None
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'best_match')  # Add this line

    try:
        carousel_items = Carousel.objects.all()[0:3]
    except Carousel.DoesNotExist:
        carousel_items = False

    products = Product.objects.all()
    
    # Apply search filter if search query exists
    if search_query:
        carousel_items = False
        matching_products = products.filter(name__icontains=search_query)
        matching_categories = Category.objects.filter(name__icontains=search_query)
        
        ''' after searching for a product and getting it, the search query will retun all the products in the founded products category'''
        products_searched_product_category = Category.objects.filter(
            categorised_products__in=matching_products
        ).distinct()
        
        products = products.filter(
            Q(name__icontains=search_query) |  
            Q(category__in=matching_categories) |  
            Q(category__in=products_searched_product_category)  
        ).distinct()

    # Apply sorting
    if sort_by == 'price_low_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_low':
        products = products.order_by('-price')
    else:  # best_match
        products = products.order_by('id')  # or any default ordering you prefer
    
    context = update_product_rating(products)
    products = context['products']
    categories_query = Category.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    items_per_page = 24
    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    dictionary = {
        'category': category,
        'products': page_obj,
        'categories': categories_query,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'current_category_slug': category_slug,
        'carousel_items': carousel_items,
        'search_query': search_query,
        'current_sort': sort_by,  # Add this line
    }
    return render(request, 'Products/list.html', context=dictionary)


def product_details(request, id, slug=None):
    product = get_object_or_404(Product, id=id, slug=slug)
    reviews = Review.objects.filter(product=product)
    
    if reviews.exists():
        total_stars = sum(review.rating for review in reviews)
        reviewer_count = reviews.count()
        avg_rating = total_stars / reviewer_count 
        
        avg_rating = float(avg_rating)
        rate = total_stars / reviewer_count
        rate = format(rate, '.1f')
        
    else:
        avg_rating = 0
        reviewer_count = 0
        rate = 0
    
    dictionary = {
        'product': product,
        'reviews': reviews,
        'reviewer': reviewer_count,
        'rates': avg_rating,
        'rate': rate,
    }
    return render(request, 'Products/details.html', context=dictionary)


def update_product_rating(products):
    for product in products:
        reviews = Review.objects.filter(product=product)
        if reviews.exists():
            total_stars = sum(review.rating for review in reviews)
            reviewer = reviews.count()
            rating = total_stars / reviewer
            product.rating = rating
            product.reviewer = reviewer
            product.save()
        else:
            product.rating = 0
            product.save()
            product.reviewer = 0

    context = {
        'products': products,

    }
    return context

''' I  must add a custom decorator to provide access to staff and superuser only '''

class ProductFormView(FormView, LoginRequiredMixin):
    template_name = 'Products/product_form.html'
    form_class = ProductForm
    success_url = '/'


    def form_valid(self, form):
        if 'new_category' in self.request.POST and self.request.POST['new_category'].strip():
            # Create new category
            category_name = self.request.POST['new_category'].strip()
            try:
                # Try to get existing category
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                # Create new category if it doesn't exist
                category = Category.objects.create(
                    name=category_name
                )
            # Set the category on the form
            form.instance.category = category
        
        form.instance.user = self.request.user
        form.save()
        messages.success(self.request, 'Product successfully added!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    

@login_required
def update_product(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id, user=user)

    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product )
        if form.is_valid():
            form.save()
            messages.success(request, 'Product successfully updated!')
            return redirect('Products:product_details', id=product.id, slug=product.slug)
        messages.error(request, 'Invalid data! Please try again with valid data.')

    return render(request, 'Products/product_form.html', {'form': form})


@login_required
def my_products(request):
    user = request.user
    try:
        if not (user.is_staff or user.is_superuser):
            messages.error(request, 'Access denied. Staff or admin privileges required.')
            return redirect('Products:product_list')
        
        products = Product.objects.filter(user=user)

        if not products:
            messages.error(request, "You haven't added any products yet.")
        context = update_product_rating(products)
        products = context['products']
        
        items_per_page = 24
        paginator = Paginator(products, items_per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'Products/my_products.html', {
            'products': page_obj,
            'is_paginated': paginator.num_pages > 1,
            'page_obj': page_obj
        })
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('Products:product_list')



class DeleteProduct(LoginRequiredMixin, DeleteView):
    model = Product
    def get_success_url(self):
        messages.success(self.request, 'Product successfully deleted!')
        return reverse_lazy('/')