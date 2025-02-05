from django.shortcuts import render, redirect,HttpResponseRedirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from Cart.models import Order,Cart, UserOrder, TotalOrder
from Products.models import Product
from .models import BillingAddress
from decimal import Decimal
from sslcommerz_python_api import SSLCSession
from dotenv import load_dotenv
import os

load_dotenv()


# Create your views here.

@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, ordered=False)
    user = request.user
    
    if request.method == 'POST':
        # Remove the commas that were creating tuples
        payment_method = request.POST.get('payment_method')
        address = request.POST.get('address')        
        city = request.POST.get('city')             
        country = request.POST.get('country')       
        zip_code = request.POST.get('postal_code')  
        
        if not all([payment_method, address, country, city, zip_code]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('Payment:checkout', order_id=order_id)
        
        try:
            # Clean up the validation logic
            items = [address, city, country, zip_code]
            
            for item in items:
                if not item or item.strip().upper() == 'NONE':
                   messages.error(request, 'Please fill in all required fields')
                   return redirect('Payment:checkout', order_id)                
                
            if not user.user_profile.is_fully_filled():
                messages.error(request, 'Please setup your profile first')
                return redirect('Profile:profile_setup')
            
            if not user.user_profile.is_name_added():
                messages.error(request, 'Please add your name in your profile.')
                return redirect('Profile:change_name')

            shipping_address = BillingAddress.objects.create(  
                order=order,
                user=user,
                address=address.strip(),  # Strip whitespace
                city=city.strip(),
                country=country.strip(),
                zip_code=zip_code.strip()
            )
            
            messages.success(request, 'Please make your payment')
            return HttpResponseRedirect(reverse('Payment:payment', kwargs={"order_id": order_id}))
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your order: {str(e)}')
            return redirect('Payment:checkout', order_id=order_id)
    
    # Get cart items and calculate totals
    cart_items = order.carts.all()
    subtotal = sum(Decimal(cart.total()) for cart in cart_items)
    total = subtotal
    
    context = {
        'order': order,
        'cart_items': cart_items,
        'subtotal': format(subtotal, '.2f'),
        'total': format(total, '.2f')
    }
    
    return render(request, 'Payment/checkout.html', context)


# Required data for payment

@login_required
def payment(request, order_id):
    user = request.user
    mypayment = SSLCSession(
    sslc_is_sandbox=True,
    sslc_store_id=os.getenv('SSLC_STORE_ID'),
    sslc_store_pass=os.getenv('SSLC_STORE_PASS'),
    )

    response_url = request.build_absolute_uri(reverse('Payment:complete', kwargs={'id': order_id}))

    mypayment.set_urls(
    success_url=response_url,
    fail_url=response_url,
    cancel_url=response_url,
    ipn_url=response_url
    )

    order = Order.objects.get(user=request.user,ordered=False, pk=order_id)
    products = order.carts.all()
    products_count = products.count()
    total = order.total()

    mypayment.set_product_integration(
    total_amount=Decimal(total),
    currency='BDT',
    product_category='Universal',
    product_name=products,
    num_of_item=products_count,
    shipping_method='Online',
    product_profile='None'
    )

    user_name = order.user.user_profile.first_name + ' ' + user.user_profile.first_name
    user_email = order.user.email
    user_address = order.user.user_profile.address
    user_address2 = order.user.user_profile.address2
    user_city = order.user.user_profile.city
    user_country = order.user.user_profile.country
    user_zip_code = order.user.user_profile.postal_code
    user_phone = order.user.user_phone_number.phone_number.as_e164


    mypayment.set_customer_info(
    name=user_name,
    email=user_email,
    address1=user_address,
    address2=user_address2,
    city=user_city, postcode=user_zip_code,
    country=user_country,
    phone=user_phone
    )

    billing_obj= BillingAddress.objects.filter(order=order).first()
    biller = user.user_profile.first_name + ' ' + user.user_profile.last_name
    billing_address = billing_obj.address
    billing_city = billing_obj.city
    billing_zip_code = billing_obj.zip_code
    billing_country = billing_obj.country

    mypayment.set_shipping_info(
    shipping_to=biller,
    address=billing_address,
    city=billing_city,
    postcode=billing_zip_code,
    country=billing_country
    )

    response_data = mypayment.init_payment()

    # You can Print the response data
    print(response_data)
    return redirect(response_data['GatewayPageURL'])


@csrf_exempt
def complete(request, id):
    if request.method == 'POST':
        payment_data = request.POST
        status = payment_data.get('status', '')      
        
        try:            
            if status == 'VALID' or status == 'SUCCESS':
                tran_id = payment_data.get('tran_id', '')
                val_id = payment_data.get('val_id', '')
                
                return redirect('Payment:purchased', tran_id=tran_id, val_id=val_id, id=id)
            
            elif status == 'FAILED':
                messages.error(request, 'Payment failed! Please try again.')
                
            elif status == 'CANCELLED':
                messages.warning(request, 'Payment cancelled! Would you like to try a different payment method?')
                
            else:
                messages.warning(request, f'Payment status: {status}. Please contact support if you need assistance.')
                
        except Exception as e:
            messages.error(request, f'An error occurred while processing your payment: {str(e)}')
            print(f"Payment processing error: {str(e)}")
            
    return redirect('Cart:user_cart')

@login_required
def purchased(request, tran_id, val_id, id):
    try:
        order = get_object_or_404(Order, id=id, user=request.user, ordered=False)
        
        # Check if order is already processed
        if order.ordered:
            messages.warning(request, "This order has already been processed.")
            return redirect('Cart:my_orders')
        
        order.ordered = True
        order.payment_id = val_id
        order.order_id = tran_id
        order.save()
        
        # Process the ordered items
        cart_items = order.carts.all()
        for cart in cart_items:
            # Update product sold count
            product = Product.objects.get(id=cart.products.id)
            product.sold += cart.quantity
            product.save()
            
            # Update user order count
            customer_order, _ = UserOrder.objects.get_or_create(user=request.user)
            customer_order.count += cart.quantity
            customer_order.save()
            
            # Update total orders count
            total_order, _ = TotalOrder.objects.get_or_create(id=1)
            total_order.count += cart.quantity
            total_order.save()
            
            # Mark cart as purchased
            cart.purchased = True
            cart.save()
        
        messages.success(request, "Payment successful! Your order has been placed.")
        return redirect('Cart:my_orders')
    
    except Exception as e:
        messages.error(request, f"Error processing order: {str(e)}")
        return redirect('Cart:user_cart')