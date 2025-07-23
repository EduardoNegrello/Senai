from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:DUDU230507@localhost/ecommerce'
db = SQLAlchemy(app)

from models import User, Product, Order

with app.app_context():
    db.create_all()

from flask import render_template  # já deve estar importado

@app.route('/')
def index():
    return render_template('HtmlZika.html')
    
# Rota de registro
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['name'], email=data['email'], password=hashed)  # <- username, não name!

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({ "id": user.id }), 201
    except Exception as e:
        db.session.rollback()
        print("Erro ao registrar:", e)
        return jsonify({ "error": str(e) }), 400

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({ "id": user.id, "name": user.username })
    return jsonify({ "error": "Credenciais inválidas" }), 401

# Listar produtos
@app.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    name = request.args.get('name')
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    return jsonify([p.to_dict() for p in query.all()])

# Criar pedido
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    order = Order(user_id=data['userId'], items=str(data['items']), total=data['total'])
    db.session.add(order)
    db.session.commit()
    return jsonify({ "orderId": order.id }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)