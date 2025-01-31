from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
from Products.models import Product
from Cart.models import Order
from .forms import ReviewForm
from django.utils import timezone

@login_required
def review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Check if the user has purchased this product within the last 30 days
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=True,
        created_at__gte=thirty_days_ago,  # Filter by order creation time
        carts__products=product
    )

    if not order_qs.exists():
        messages.error(request, 'You can only review products purchased within the last 30 days.')
        return redirect('product_list')  # Or redirect to a more appropriate page

    # Check if user has already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this product.')
        return redirect('product_list') # Or redirect to a more appropriate page

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Review submitted successfully')
            return redirect('Products:product_details', id=product.id, slug=product.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product,
    }

    return render(request, 'Review/review.html', context)