from app import create_app, db
from app.models import User, Product
import os

app = create_app()

with app.app_context():
    print("Menghapus database lama (jika ada)...")
    if os.path.exists('app/site.db'):
        os.remove('app/site.db')
        
    print("Membuat database baru...")
    db.create_all()

    print("Membuat user admin...")
    admin_user = User(username='admin', email='admin@example.com', is_admin=True)
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    print("Membuat user biasa...")
    test_user = User(username='testuser', email='test@example.com')
    test_user.set_password('password123')
    db.session.add(test_user)

    print("Menambahkan produk sampel...")
    products = [
        Product(name='Classic T-Shirt', description='A comfortable and stylish classic t-shirt.', price=250000, stock=50, image_file='tshirt.jpg'),
        Product(name='Slim Fit Jeans', description='Modern slim fit jeans for everyday wear.', price=750000, stock=30, image_file='jeans.jpg'),
        Product(name='Running Shoes', description='Lightweight and durable running shoes.', price=1200000, stock=20, image_file='shoes.jpg'),
        Product(name='Leather Jacket', description='A timeless leather jacket for a cool look.', price=2500000, stock=15, image_file='jacket.jpg'),
        Product(name='Stylish Hoodie', description='Warm and stylish hoodie for casual outings.', price=600000, stock=40, image_file='hoodie.jpg'),
        Product(name='Formal Shirt', description='A sharp formal shirt for professional settings.', price=450000, stock=25, image_file='shirt.jpg')
    ]
    db.session.bulk_save_objects(products)

    db.session.commit()
    print("Database berhasil dibuat dan diisi dengan data sampel!")
    print("\nCredentials Admin:")
    print("Username: admin")
    print("Password: admin123")