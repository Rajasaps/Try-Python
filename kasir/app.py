from flask import Flask, render_template, jsonify, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kedai-hauna-secret-key-2024'

# Data menu makanan
menu_items = [
    {"id": 1, "name": "Bakso Malang", "price": 23000, "image": "/static/images/Bakso malang.jpg"},
    {"id": 2, "name": "Seblak Special", "price": 16000, "image": "/static/images/Seblak special.jpg"},
    {"id": 3, "name": "Mie Ayam", "price": 18000, "image": "/static/images/Mie Ayam.jpg"},
    {"id": 4, "name": "Siomay", "price": 11000, "image": "/static/images/Siomay.jpg?v=2"},
    {"id": 5, "name": "Tea", "price": 6000, "image": "/static/images/Tea.jpg", "has_variant": True, "variants": ["Dingin", "Hangat"]},
    {"id": 6, "name": "Ayam Crispy", "price": 17000, "image": "/static/images/Ayam Crispy.jpg"},
    {"id": 7, "name": "Nasi", "price": 5000, "image": "/static/images/Nasi.jpg"},
]

@app.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = []
    return render_template('index.html', menu_items=menu_items)

@app.route('/api/menu')
def get_menu():
    return jsonify(menu_items)

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', [])
    return jsonify(cart)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    item_id = data.get('id')
    variant = data.get('variant', '')
    
    # Cari item di menu
    menu_item = next((item for item in menu_items if item['id'] == item_id), None)
    if not menu_item:
        return jsonify({'error': 'Item tidak ditemukan'}), 404
    
    # Ambil cart dari session
    cart = session.get('cart', [])
    
    # Buat unique key untuk item dengan varian
    item_key = f"{item_id}_{variant}" if variant else str(item_id)
    
    # Cek apakah item dengan varian yang sama sudah ada di cart
    existing_item = next((item for item in cart if item.get('item_key') == item_key), None)
    
    if existing_item:
        existing_item['quantity'] += 1
    else:
        item_name = f"{menu_item['name']} ({variant})" if variant else menu_item['name']
        cart.append({
            'id': menu_item['id'],
            'item_key': item_key,
            'name': item_name,
            'price': menu_item['price'],
            'image': menu_item['image'],
            'quantity': 1,
            'variant': variant
        })
    
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    data = request.json
    item_id = data.get('id')
    quantity = data.get('quantity')
    
    cart = session.get('cart', [])
    item = next((item for item in cart if item['id'] == item_id), None)
    
    if item:
        if quantity <= 0:
            cart.remove(item)
        else:
            item['quantity'] = quantity
    
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.json
    item_id = data.get('id')
    
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != item_id]
    
    session['cart'] = cart
    return jsonify({'success': True, 'cart': cart})

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({'success': True})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    data = request.json
    payment_method = data.get('payment_method', 'cash')
    
    if not cart:
        return jsonify({'error': 'Keranjang kosong'}), 400
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    tax = subtotal * 0.1
    total = subtotal + tax
    
    # Simpan transaksi (dalam aplikasi nyata, simpan ke database)
    transaction = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'items': cart,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'payment_method': payment_method,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Clear cart setelah checkout
    session['cart'] = []
    
    return jsonify({
        'success': True,
        'transaction': transaction,
        'message': 'Pembayaran berhasil!'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
