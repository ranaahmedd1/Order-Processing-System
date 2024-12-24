import  flask 
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from mysql import connector
app=flask.Flask("app")

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/ordering'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # orders = db.relationship('Order', backref='user', lazy=True)


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_list = db.Column(db.Text, nullable=False)  
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 

with app.app_context():
    db.create_all()


@app.route('/place_order/', methods=['POST'])
def place_order():
    data = request.get_json()  
    if not data:
        return {"error": "Invalid JSON or empty body"}, 400

    product_name= data.get('product_name')

    quantity = data.get('quantity')

    if not product_name or not quantity:
        return {"error": "Product name and quantity are required"}, 400

    # Fetch the product from the database
    product = Products.query.filter_by(name=product_name).first()
    if not product:
        return {"error": "Product not found"}, 404

    # Check stock availability
    if product.stock_quantity < quantity:
        return {"error": "Insufficient stock"}, 400

    total_price = product.price * quantity

    # Deduct stock and create the order
    product.stock_quantity -= quantity
    new_order = Order(product_id=product.id, quantity=quantity, total_price=total_price, status="Completed")
    db.session.add(new_order)
    db.session.commit()

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "product_name": product.name,
        "quantity": quantity,
        "total_price": total_price,
        "remaining_stock": product.stock_quantity
    }, 200


