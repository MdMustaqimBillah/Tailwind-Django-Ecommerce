from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Cart.models import Cart, Order
from .forms import OrderForm
from Products.models import Product
from Profile.models import PhoneNumber
from Payment.models import BillingAddress
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template

@login_required
def user_cart(request):
    user=request.user
    cart_items = Cart.objects.filter(user=user, purchased=False)
    subtotal = sum(float(item.total()) for item in cart_items)
    shipping = len(cart_items)*65
    tax= float(subtotal *.15)
    total = subtotal +  shipping + tax
    
    context = {
        'cart_items': cart_items,
        'subtotal': format(subtotal, '.2f'),
        'shipping': format(shipping, '.2f'),
        'tax': format(tax, '.2f'),
        'total': format(total, '.2f'),
    }
    
    return render(request, 'Cart/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        carts = Cart.objects.filter(
            user=request.user,
            products=product,
            purchased=False
        ).first()

        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.carts.filter(products=product).exists():
                carts.quantity += quantity
                carts.save()
                messages.info(request, 'Product already added to cart')
            else:
                order.carts.add(carts)
                messages.success(request, 'Added to cart successfully!')
        
        if carts:
            cart_item = carts
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item = Cart.objects.create(
                user=request.user,
                products=product,
                quantity=quantity
            )
        
    carts = Cart.objects.filter(user=request.user, purchased=False)
    
    subtotal = sum(float(item.total()) for item in carts)
    shipping = len(carts) * 65
    tax = float(subtotal * .15)
    total = subtotal + shipping + tax
    
    context = {
        'cart_items': carts,
        'subtotal': format(subtotal, '.2f'),
        'shipping': format(shipping, '.2f'),
        'tax': format(tax, '.2f'),
        'total': format(total, '.2f'),
    }
    
    return render(request, 'Cart/cart.html', context)


@login_required
def proceed_to_checkout(request, product_id=None):
    phone_number = PhoneNumber.objects.filter(user=request.user)

    # Phone number verification check
    if not phone_number.exists():
        messages.error(request, 'Please add a phone number to proceed')
        return redirect('Profile:verification')
    if not phone_number.first().is_verified:
        messages.error(request, 'Please verify your phone number to proceed')
        return redirect('Profile:resend_code')

    # Handling direct product purchase (buy now)
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = Cart.objects.create(
            user=request.user,
            products=product,
            quantity=quantity
        )
        
        order = Order.objects.create(
            user=request.user,
            ordered=False
        )
        order.carts.add(cart_item)
        
        order.order_id = f"TEMP-{order.id}-{order.created_at.strftime('%Y%m%d')}"
        order.save()
        
        return redirect('Payment:checkout', order_id=order.id)

    # Handling cart checkout
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    
    try:
        order = Order.objects.create(
            user=request.user,
            ordered=False
        )
        
        order.carts.add(*cart_items)
                
        order.order_id = f"TEMP-{order.id}-{order.created_at.strftime('%Y%m%d')}"
        order.save()
        
        return redirect('Payment:checkout', order_id=order.id)
    
    except Exception as e:
        messages.error(request, 'An error occurred while processing your checkout.')
        return redirect('Cart:user_cart')
    


@login_required
def increment (request, pk):
    user=request.user
    cart_item = get_object_or_404(Cart, id=pk, user=user)
    cart_item.quantity += 1

    cart_item.save()
    return redirect('Cart:user_cart')

@login_required
def decrement (request, pk):
    user=request.user
    cart_item = get_object_or_404(Cart, id=pk, user=user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('Cart:user_cart')


@login_required
def remove_from_cart(request, pk):
    user=request.user
    cart_item = get_object_or_404(Cart, id=pk, user=user)
    cart_item.delete()
    messages.info(request, 'Item removed from cart successfully')
    
    return redirect('Cart:user_cart')


class OrderSummaryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'Cart/order.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, ordered=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add review status for each cart item
        for order in context['orders']:
            for cart_item in order.carts.all():
                cart_item.has_reviewed = cart_item.products.product_reviews.filter(user=self.request.user).exists()
        
        context['cart_items'] = Cart.objects.filter(user=self.request.user, purchased=True)
        return context    

@login_required
def download_invoice(request, order_id):

    if not (request.user.is_staff or request.user.is_superuser):

        order = get_object_or_404(Order, id=order_id, user=request.user, ordered=True)
        try:
            billing_address = BillingAddress.objects.get(user=request.user, order=order)
            subtotal = sum(float(cart.total()) for cart in order.carts.all())
            shipping = len(order.carts.all()) * 0
            total = subtotal + shipping
        except BillingAddress.DoesNotExist:
            messages.error(request,'Please fill your billing address and update your profile.')
        except Exception as e:
        # Handle other potential exceptions (e.g., related cart items not found)
            return HttpResponse(f"An error occurred: {e}", status=500)

    else:
        order = get_object_or_404(Order, id=order_id, ordered=True)
        customer = order.user
        try:
            billing_address = BillingAddress.objects.get(user=customer, order=order)
            subtotal = sum(float(cart.total()) for cart in order.carts.all())
            shipping = len(order.carts.all()) * 0
            total = subtotal + shipping
        except BillingAddress.DoesNotExist:
            messages.error(request,'Please fill your billing address and update your profile.')
        except Exception as e:
        # Handle other potential exceptions (e.g., related cart items not found)
            return HttpResponse(f"An error occurred: {e}", status=500)


    
    template_path = 'Cart/invoice_template.html'
    context = {
        'order': order,
        'cart_items': order.carts.all(),
        'billing_address': billing_address,
        'subtotal': format(subtotal, '.2f'),
        'shipping': format(shipping, '.2f'),
        'total': format(total, '.2f'),
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'  # Use attachment for download

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=lambda uri, rel: uri
    )

    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response


@login_required
def delivered_orders(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied! Admin and staff permission only.')
        return redirect('product_list')
    orders = Order.objects.filter(ordered=True, delivered=True)
    return render(request, 'Cart/delivered_orders.html', {'orders': orders})

@login_required
def pending_orders(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied! Admin and staff permission only.')
        return redirect('product_list')
    orders = Order.objects.filter(ordered=True, delivered=False)
    return render(request, 'Cart/pending_orders.html', {'orders': orders})


@login_required
def detail_delivered_order(request,order_id):
    user=request.user
    if not (user.is_staff or user.is_superuser):
        messages.error(request, 'Access denied! Admin and staff permission only.')
        return redirect('product_list')
 
    order = Order.objects.get(id=order_id)
    total = sum(float(cart.total()) for cart in order.carts.all())

    context = {'order': order,
               'order_id': order.id,
               'total':total,
               'subtotal':total
               }
    
    return render(request, 'Cart/detail_delivered_order.html', context=context)

@login_required
def detail_pending_order(request,order_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied! Admin and staff permission only.')
        return redirect('product_list')

    order = Order.objects.get(pk=order_id)
    total = sum(float(cart.total()) for cart in order.carts.all())

    form=OrderForm(instance=order)
    if request.method == 'POST':
        form=OrderForm(request.POST, instance=order)
        if form.is_valid():
            order.delivered = True
            form.save()
            messages.success(request, 'Order delivered successfully.')
            return redirect('Cart:pending_orders')
        
    context = {'order': order,
               'order_id': order.id,
               'total':total,
               'subtotal':total
               }

    return render(request, 'Cart/detail_pending_order.html', context=context)


@login_required
def invoice_for_admins(request, order_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied! Admin and staff permission only.')
        return redirect('product_list')

    order = Order.objects.get(pk=order_id)
    customer = order.user
    address = BillingAddress.objects.get(order=order, user=customer)
    pass