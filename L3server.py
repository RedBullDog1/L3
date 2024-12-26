from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(100), nullable=False)
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return username
def create_default_user():
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('password')
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default user 'admin' created with password 'password'.")
    else:
        print("Default user 'admin' already exists.")

# Resource for all items
class ItemList(Resource):
    def get(self):
        items = Item.query.all()
        return jsonify([
            {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'size': item.size,
                'weight': item.weight,
                'color': item.color
            } for item in items
        ])

    @auth.login_required
    def post(self):
        data = request.get_json()
        required_fields = ('name', 'price', 'size', 'weight', 'color')
        if not all(field in data for field in required_fields):
            return {'message': 'Missing fields'}, 400
        new_item = Item(
            name=data['name'],
            price=data['price'],
            size=data['size'],
            weight=data['weight'],
            color=data['color']
        )
        db.session.add(new_item)
        db.session.commit()
        return {'message': 'Item created', 'id': new_item.id}, 201
class ItemResource(Resource):
    def get(self, id):
        item = Item.query.get_or_404(id)
        return jsonify({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'size': item.size,
            'weight': item.weight,
            'color': item.color
        })
    @auth.login_required
    def put(self, id):
        item = Item.query.get_or_404(id)
        data = request.get_json()
        for field in ('name', 'price', 'size', 'weight', 'color'):
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        return {'message': 'Item updated'}
    @auth.login_required
    def delete(self, id):
        item = Item.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted'}
api.add_resource(ItemList, '/items')
api.add_resource(ItemResource, '/items/<int:id>')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_user()
    app.run(debug=True)
