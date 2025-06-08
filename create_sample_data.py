from app import create_app, db
from app.models import User, Product
import os

app = create_app()

with app.app_context():
    db_path = os.path.join(os.path.dirname(__file__), 'app', 'site.db')
    print("Menghapus database lama (jika ada)...")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Membuat database baru...")
    db.create_all()

    print("Membuat user admin...")
    admin_user = User(username='admin', email='admin@atherz.co', is_admin=True)
    admin_user.set_password('admin123')
    db.session.add(admin_user)

    print("Membuat user biasa...")
    test_user = User(username='testuser', email='test@example.com')
    test_user.set_password('password123')
    db.session.add(test_user)

    print("Menambahkan produk sampel...")
    products = [
        Product(name='Urban Explorer T-Shirt', description='T-shirt katun premium yang nyaman untuk petualangan harian di kota.', price=299000, stock=50, image_file='product1.jpg'),
        Product(name='Slim-Fit Chino Pants', description='Celana chino modern dengan potongan slim-fit, cocok untuk gaya kasual dan semi-formal.', price=599000, stock=30, image_file='product2.jpg'),
        Product(name='Vertex Performance Sneakers', description='Sneakers ringan dengan desain futuristik, memberikan kenyamanan maksimal.', price=1250000, stock=20, image_file='product3.jpg'),
        Product(name='Maverick Aviator Jacket', description='Jaket kulit sintetis dengan gaya aviator klasik yang tak lekang oleh waktu.', price=1899000, stock=15, image_file='product4.jpg'),
        Product(name='Stealth Tech Hoodie', description='Hoodie dengan bahan teknis yang tahan air dan angin, dilengkapi banyak saku fungsional.', price=799000, stock=40, image_file='product5.jpg'),
        Product(name='Prestige Formal Shirt', description='Kemeja formal dengan bahan premium yang tidak mudah kusut untuk tampilan profesional.', price=499000, stock=25, image_file='product6.jpg'),
        Product(name='Nomad Cargo Shorts', description='Celana pendek kargo yang tahan lama dengan banyak kantong untuk semua kebutuhanmu.', price=349000, stock=60, image_file='product7.jpg'),
        Product(name='Azure Denim Jacket', description='Jaket denim dengan warna biru pudar yang klasik, mudah dipadupadankan.', price=899000, stock=22, image_file='product8.jpg')
    ]
    db.session.bulk_save_objects(products)

    db.session.commit()
    print("\nDatabase ATHERZ.CO berhasil dibuat dan diisi dengan data sampel!")
    print("\nCredentials Admin:")
    print("Email: admin@atherz.co")
    print("Password: admin123")