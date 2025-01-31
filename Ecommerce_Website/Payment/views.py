from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Cart.models import Order,Cart, UserOrder, TotalOrder
from Products.models import Product 
from .models import BillingAddress
from decimal import Decimal

# Create your views here.

@login_required
def checkout(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user, ordered=False)
    user = request.user
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        address = request.POST.get('address'),
        city = request.POST.get('city'),
        country = request.POST.get('country'),
        zip_code = request.POST.get('postal_code')
        
        if not all([ payment_method, address, country, city, zip_code]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('Payment:checkout', order_id=order_id)
        
        
        try:

            items = [address, city, country, zip_code]
            
            for item in items:
                item_str = str(item[0]).strip().upper()
    
                if not item_str or item_str == 'NONE':
                   messages.error(request, 'Please fill in all required fields')
                   return redirect('Payment:checkout', order_id)                
                
                
            if not user.user_profile.is_fully_filled():
                messages.error(request, 'Please setup your profile first')
                return redirect('Profile:profile_setup')
            
            if not user.user_profile.is_name_added():
                messages.error(request, 'Please add your name in your profile.')
                return redirect('Profile:change_name')


            shipping_address = BillingAddress.objects.create(  
            order = order,
            user = user,
            address = address,
            city = city,
            country = country,
            zip_code = zip_code

            )

            order.order_id = f"ORD-{order.id}-{order.created_at.strftime('%Y%m%d')}"
            
            for cart in order.carts.all():
                product_id = cart.products.id
                product = Product.objects.get_or_create(id=product_id)
                product[0].sold += cart.quantity
                product[0].save()
                customer_order = UserOrder.objects.get_or_create(user=request.user)
                customer_order[0].count += cart.quantity
                customer_order[0].save()
                total_order, created = TotalOrder.objects.get_or_create(id=1)
                total_order.count += cart.quantity
                total_order.save()
                cart.purchased = True
                cart.save()
            
            order.ordered = True
            order.save()
            
            
            messages.success(request, 'Order placed successfully!')
            return redirect('/', order_id=order.id)
            
        except Exception as e:
            messages.error(request, 'An error occurred while processing your order')
            return redirect('Payment:checkout', order_id=order_id)
    
    cart_items = order.carts.all()
    subtotal = sum(Decimal(cart.total()) for cart in cart_items )
    shipping_cost = len(cart_items) * 0 
    total = subtotal + shipping_cost
    
    context = {
        'order': order,
        'cart_items': cart_items,
        'subtotal': format(subtotal, '.2f'),
        'shipping_cost': format(shipping_cost, '.2f'),
        'total': format(total, '.2f')
    }
    
    return render(request, 'Payment/checkout.html', context)
