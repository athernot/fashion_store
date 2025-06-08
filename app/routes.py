from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from app import db
from app.models import Product, User, Order, OrderItem
from app.forms import RegistrationForm, LoginForm, CheckoutForm
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

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
        flash('Your account has been created! You are now able to log in', 'success')
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
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    session.pop('cart', None)
    return redirect(url_for('main.home'))

@main.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    session.modified = True
    flash('Product added to cart!', 'success')
    return redirect(request.referrer or url_for('main.catalog'))

@main.route("/cart")
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', display_cart={}, total=0)

    cart_items = session.get('cart', {})
    display_cart = {}
    total = 0

    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            total += product.price * quantity
            display_cart[product] = quantity
    
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
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('main.catalog'))

    display_cart = {}
    total_price = 0
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            total_price += product.price * quantity
            display_cart[product] = quantity

    if form.validate_on_submit():
        new_order = Order(total_price=total_price, customer=current_user)
        db.session.add(new_order)
        db.session.commit()

        for product, quantity in display_cart.items():
            order_item = OrderItem(quantity=quantity, price_per_item=product.price, product_id=product.id, order_id=new_order.id)
            product.stock -= quantity # Kurangi stok
            db.session.add(order_item)

        db.session.commit()
        session.pop('cart', None)
        flash('Your order has been placed!', 'success')
        return redirect(url_for('main.order_success'))

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
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    
    total_users = User.query.count()
    total_orders = Order.query.count()
    recent_orders = Order.query.order_by(Order.date_posted.desc()).limit(5).all()
    low_stock_products = Product.query.filter(Product.stock <= 10).all()

    stats = {
        'total_users': total_users,
        'total_orders': total_orders,
    }
    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats, recent_orders=recent_orders, low_stock_products=low_stock_products)

@main.route("/contact")
def contact():
    return render_template('contact.html', title='Contact Us')