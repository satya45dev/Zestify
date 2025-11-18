from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout 
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q 
# Forms and Models
from .forms import AddressForm, AddCardForm, AddUPIForm, AccountSettingsForm # <-- ADDED AccountSettingsForm
from .models import Order, Product, Category, Wishlist, Address, SavedCard, SavedUPI 
from .cart import Cart

# --- SHARED CONTEXT FUNCTION ---
def get_shared_context(request):
    """Initializes the cart and fetches all categories."""
    cart = Cart(request) 
    categories = Category.objects.all()
    return {'cart': cart, 'categories': categories}

# --- PRODUCT AND SHOP VIEWS ---

def search_results(request):
    """
    Handles product search functionality based on query parameters.
    It renders the results using the index.html template.
    """
    context = get_shared_context(request)
    query = request.GET.get('q') 
    products = Product.objects.all()
    
    if query:
        search_query = (
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
        products = products.filter(search_query).distinct()

    context.update({
        'products': products,
        'query': query, 
        'hide_hero': True, 
    })
    
    return render(request, 'index.html', context)


def product_detail(request, product_id):
    """Renders the single product detail page."""
    product = get_object_or_404(Product, id=product_id)
    context = get_shared_context(request)
    
    context.update({
        'product': product,
        'hide_hero': True,
    })
    
    return render(request, 'product_detail.html', context)

def index(request):
    context = get_shared_context(request)
    products = Product.objects.all() 
    
    context.update({
        'products': products,
    })
    
    return render(request, 'index.html', context)

def category_detail(request, slug):
    """Fetches products filtered by the selected category slug."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    context = get_shared_context(request)
    
    context.update({
        'products': products,
        'active_category': category.name,
        'hide_hero': True 
    })
    
    return render(request, 'index.html', context)

# --- AUTHENTICATION VIEWS ---

def login_view(request):
    if request.method == 'POST':
        user_input = request.POST['username'] 
        password = request.POST['password']
        username_to_auth = user_input 

        if '@' in user_input:
            try:
                user_obj = User.objects.get(email=user_input)
                username_to_auth = user_obj.username 
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
                return redirect('login')

        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back!")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Incorrect password.")
            return redirect('login')

    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('user_register') 
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
            return redirect('user_register') 

        if User.objects.filter(email=email).exists():
            messages.error(request, "That email is already in use.")
            return redirect('user_register') 

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'register.html')

@login_required(login_url='/login/') 
def user_dashboard(request):
    user = request.user
    try:
        recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    except:
        recent_orders = [] 
    
    context = {
        'user': user,
        'orders': recent_orders,
        'loyalty_points': 120,
        'cart': Cart(request),
    }
    return render(request, 'dashboard.html', context)

# --- CART VIEWS ---

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart_detail.html', {'cart': cart})

@login_required(login_url='/login/')
def checkout_view(request):
    cart = Cart(request)
    
    if not cart:
        messages.error(request, "Your cart is empty and cannot be checked out.")
        return redirect('cart_detail')

    if request.method == 'POST':
        return redirect('process_payment') 

    return render(request, 'checkout.html', {'cart': cart})

@login_required(login_url='/login/')
def process_payment(request):
    """Handles payment method selection and final order creation."""
    cart = Cart(request)

    if not cart:
        messages.error(request, "Your cart is empty and cannot be processed.")
        return redirect('cart_detail')

    if request.method == 'POST':
        user = request.user
        total_price = cart.get_total_price()
        
        product_summary = [f"{item['quantity']}x {item['product'].name}" for item in cart]
        product_names = "\n".join(product_summary)

        order = Order.objects.create( 
            user=user,
            product_names=product_names,
            total_price=total_price
        )

        cart.clear() 

        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'payment.html', {'cart': cart})

@login_required(login_url='/login/')
def order_confirmation(request, order_id):
    """Shows a thank you page with basic order summary."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_summary': order.product_names.split('\n'),
        'categories': Category.objects.all(), 
        'cart': Cart(request), 
    }
    
    return render(request, 'order_confirmation.html', context)

# --- WISHLIST VIEWS ---

@login_required(login_url='/login/')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, f"{product.name} added to your wishlist!")
    else:
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from your wishlist.")

    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required(login_url='/login/')
def wishlist_view(request):
    """Shows all products saved by the current user."""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'title': 'My Wishlist',
        'wishlist_items': wishlist_items,
        **get_shared_context(request) 
    }
    return render(request, 'wishlist.html', context)


# --- DASHBOARD ACTION VIEWS ---

@login_required(login_url='/login/')
def track_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'title': 'Track Orders', 
        'orders': orders, 
    }
    return render(request, 'track_orders.html', context)

@login_required(login_url='/login/')
def my_addresses_view(request):
    """Fetches and displays the user's saved addresses."""
    user_addresses = Address.objects.filter(user=request.user)
    
    context = get_shared_context(request) 
    context.update({
        'title': 'My Addresses', 
        'addresses': user_addresses,
    })
    return render(request, 'my_addresses.html', context)

@login_required(login_url='/login/')
def add_address_view(request):
    """Handles adding a new address."""
    context = get_shared_context(request)
    
    if request.method == 'POST':
        form = AddressForm(request.POST) 
        
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.country = 'India' # Set the country, as it's not exposed in the simple form
            address.save()
            messages.success(request, "New address added successfully!")
            return redirect('my_addresses')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddressForm()

    context.update({
        'title': 'Add New Address',
        'form': form,
        'hide_hero': True,
    })
    return render(request, 'add_address.html', context)

@login_required(login_url='/login/')
def payment_methods_view(request):
    """Fetches and displays the user's saved payment methods."""
    context = get_shared_context(request)
    
    saved_cards = SavedCard.objects.filter(user=request.user)
    saved_upis = SavedUPI.objects.filter(user=request.user)
    
    context.update({
        'title': 'Payment Methods',
        'saved_cards': saved_cards,
        'saved_upis': saved_upis,
    })
    
    return render(request, 'payment_methods.html', context)


@login_required(login_url='/login/')
def add_payment_method_view(request, method_type):
    """Handles adding a new card or UPI ID."""
    context = get_shared_context(request)
    
    if method_type == 'card':
        form_class = AddCardForm
        redirect_url = 'payment_methods' 
    elif method_type == 'upi':
        form_class = AddUPIForm
        redirect_url = 'payment_methods' 
    else:
        messages.error(request, "Invalid payment method type.")
        return redirect('payment_methods')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            # Special handling for card to only save last 4 digits
            if method_type == 'card':
                card = form.save(commit=False)
                full_card_number = form.cleaned_data['full_card_number']
                card.card_number_last_four = full_card_number[-4:]
                card.card_type = 'Visa' # Placeholder
                
                # Check if this is the first card; if so, make it default
                if not SavedCard.objects.filter(user=request.user).exists():
                    card.is_default = True
                
                card.user = request.user
                card.save()
                messages.success(request, f"Card ending in {card.card_number_last_four} saved successfully.")
            
            # Handling for UPI
            elif method_type == 'upi':
                upi = form.save(commit=False)
                upi.user = request.user
                
                # Check if this is the first UPI; if so, make it default
                if not SavedUPI.objects.filter(user=request.user).exists():
                    upi.is_default = True
                    
                upi.save()
                messages.success(request, f"UPI ID {upi.upi_id} saved successfully.")
                
            return redirect(redirect_url)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = form_class()

    context.update({
        'title': f"Add New {'Card' if method_type == 'card' else 'UPI ID'}",
        'form': form,
        'method_type': method_type,
    })
    return render(request, 'add_payment_method.html', context)

@login_required(login_url='/login/')
def delete_card_view(request, card_id):
    """Deletes a saved card."""
    card = get_object_or_404(SavedCard, id=card_id, user=request.user)
    
    # Check if the card being deleted is the default
    if card.is_default:
        # If it's the default, try to set a new default before deleting
        remaining_cards = SavedCard.objects.filter(user=request.user).exclude(id=card_id).order_by('-id')
        if remaining_cards.exists():
            new_default = remaining_cards.first()
            new_default.is_default = True
            new_default.save()

    card.delete()
    messages.success(request, f"Card ending in ****{card.card_number_last_four} has been removed.")
    
    return redirect('payment_methods')


@login_required(login_url='/login/')
def set_default_card_view(request, card_id):
    """Sets a specific saved card as the default for the user."""
    card_to_set = get_object_or_404(SavedCard, id=card_id, user=request.user)
    
    # 1. Unset the current default card
    SavedCard.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # 2. Set the new card as default
    card_to_set.is_default = True
    card_to_set.save()
    
    messages.success(request, f"Card ending in ****{card_to_set.card_number_last_four} is now your default payment card.")
    return redirect('payment_methods')


@login_required(login_url='/login/')
def delete_upi_view(request, upi_id):
    """Deletes a saved UPI ID."""
    upi = get_object_or_404(SavedUPI, id=upi_id, user=request.user)

    # Check if the UPI being deleted is the default
    if upi.is_default:
        # If it's the default, try to set a new default before deleting
        remaining_upis = SavedUPI.objects.filter(user=request.user).exclude(id=upi_id).order_by('-id')
        if remaining_upis.exists():
            new_default = remaining_upis.first()
            new_default.is_default = True
            new_default.save()

    upi.delete()
    messages.success(request, f"UPI ID '{upi.upi_id}' has been removed.")
    
    return redirect('payment_methods')


@login_required(login_url='/login/')
def set_default_upi_view(request, upi_id):
    """Sets a specific saved UPI ID as the default for the user."""
    upi_to_set = get_object_or_404(SavedUPI, id=upi_id, user=request.user)
    
    # 1. Unset the current default UPI
    SavedUPI.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # 2. Set the new UPI as default
    upi_to_set.is_default = True
    upi_to_set.save()
    
    messages.success(request, f"UPI ID '{upi_to_set.upi_id}' is now your default UPI ID.")
    return redirect('payment_methods')

@login_required(login_url='/login/')
def account_settings_view(request):
    """Handles updating the user's profile details."""
    context = get_shared_context(request)
    
    if request.method == 'POST':
        # Populate form with POST data and the instance (current user)
        form = AccountSettingsForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Account details updated successfully!")
            return redirect('account_settings')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Initial GET request: populate form with current user data
        form = AccountSettingsForm(instance=request.user)

    context.update({
        'title': 'Account Settings',
        'form': form,
    })
    
    # Renders the new dedicated template
    return render(request, 'account_settings.html', context)
    
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('index')