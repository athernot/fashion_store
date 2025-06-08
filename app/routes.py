from flask import render_template, url_for, flash, redirect, request, Blueprint, session, abort
from app import db
from app.models import Product, User, Order, OrderItem
from app.forms import RegistrationForm, LoginForm, CheckoutForm
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

main = Blueprint('main', __name__)

# Decorator untuk admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route("/")
@main.route("/home")
def home():
    products = Product.query.limit(4).all()
    return render_template('home.html', products=products)

@main.route("/catalog")
def catalog():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=6)
    return render_template('catalog.html', products=products, title='Catalog')

@main.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', title=product.name, product=product)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    session.pop('cart', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)

    if product.stock > cart.get(product_id_str, 0):
        cart[product_id_str] = cart.get(product_id_str, 0) + 1
        session.modified = True
        flash(f'{product.name} has been added to your cart!', 'success')
    else:
        flash(f'Sorry, {product.name} is out of stock!', 'warning')
    return redirect(request.referrer or url_for('main.catalog'))

def get_cart_details():
    cart_items = session.get('cart', {})
    display_cart = {}
    total = 0
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            total += product.price * quantity
            display_cart[product] = quantity
    return display_cart, total

@main.route("/cart")
def cart():
    display_cart, total = get_cart_details()
    if not display_cart:
        return render_template('cart.html', title='Shopping Cart')
    return render_template('cart.html', title='Shopping Cart', display_cart=display_cart, total=total)

@main.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    product_id_str = str(product_id)
    if 'cart' in session and product_id_str in session['cart']:
        session['cart'].pop(product_id_str)
        session.modified = True
        flash('Product removed from cart.', 'info')
    return redirect(url_for('main.cart'))

@main.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    display_cart, total_price = get_cart_details()
    
    if not display_cart:
        flash('Your cart is empty. Please add items before checking out.', 'info')
        return redirect(url_for('main.catalog'))

    if form.validate_on_submit():
        # Buat pesanan baru
        new_order = Order(
            total_price=total_price, 
            customer=current_user,
            shipping_name=form.name.data,
            shipping_address=form.address.data,
            shipping_phone=form.phone.data
        )
        db.session.add(new_order)
        # Commit untuk mendapatkan ID pesanan
        db.session.commit()

        # Buat item pesanan dan kurangi stok
        for product, quantity in display_cart.items():
            order_item = OrderItem(
                quantity=quantity, 
                price_per_item=product.price, 
                product_id=product.id, 
                order_id=new_order.id
            )
            db.session.add(order_item)
            # Kurangi stok produk
            product.stock -= quantity
        
        db.session.commit()
        session.pop('cart', None)
        flash('Thank you! Your order has been placed successfully!', 'success')
        return redirect(url_for('main.order_success', order_id=new_order.id))

    return render_template('checkout.html', title='Checkout', form=form, display_cart=display_cart, total=total_price)

@main.route("/order_success")
@login_required
def order_success():
    return render_template('order_success.html', title='Order Successful')

@main.route("/profile")
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date_posted.desc()).all()
    return render_template('profile.html', title='My Profile', orders=orders)

@main.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    recent_orders = Order.query.order_by(Order.date_posted.desc()).limit(5).all()
    low_stock_products = Product.query.filter(Product.stock <= 10).all()

    stats = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    }
    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats, recent_orders=recent_orders, low_stock_products=low_stock_products)

@main.route("/contact")
def contact():
    return render_template('contact.html', title='Contact Us')