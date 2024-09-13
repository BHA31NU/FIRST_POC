from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:bhanu.2640B@localhost/flask_database'
app.config['SECRET_KEY'] = '7964728f8dacfe03df5bc5adb0852220e0c62164e3c452c0'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50))  # Optional field for the user's name
    phone_number = db.Column(db.String(15))  # Optional field for phone number

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        login_user(user)
        return jsonify(message="Login successful"), 200
    return jsonify(message="Invalid credentials"), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify(message="User already exists"), 400
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_user = User(
        username=data.get('username'),
        password=hashed_password,
        name=data.get('name'),  # Ensure name is provided
        phone_number=data.get('phone_number')  # Ensure phone_number is provided
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User registered successfully"), 201

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify(message="Logout successful"), 200

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify(message=f"Welcome, {current_user.username}!"), 200

@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'name': user.name, 'phone_number': user.phone_number} for user in users]
    return jsonify(user_list), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)s