import datetime
import jwt
import flask
import database
from json import JSONEncoder
from marshmallow import Schema, fields, ValidationError
from flask_httpauth import HTTPTokenAuth

SECRET_KEY = 'randomly_generate_key_using_os_urandom_stored_in_env'


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class CustomerSchema(Schema):
    name = fields.Str(required=True, validate=must_not_be_blank)
    dob = fields.Date(required=True, format="%Y-%m-%d")


class UserSchema(Schema):
    username = fields.Str(required=True, validate=must_not_be_blank)
    password = fields.Str(required=True, validate=must_not_be_blank)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.json_encoder = CustomJSONEncoder
auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def validate_auth_jwt(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms='HS256')
        # Optional: Check if token is blacklisted in database
        return True
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return False


@app.route('/', methods=['GET'])
def home():
    return "<h1>Customer CRUD API</h1>"


@app.route('/version', methods=['GET'])
def server_version():
    return database.get_server_version()


@app.route('/api/customers', methods=['GET'])
@auth.login_required
def get_all_customers():
    n_youngest = flask.request.args.get('n', default=0, type=int)
    return flask.jsonify(database.get_all_customers(n_youngest))


@app.route('/api/customers', methods=['POST'])
@auth.login_required
def add_new_customer():
    json_data = flask.request.get_json()
    if not json_data:
        return {'message': 'No input data'}, 400

    customer_schema = CustomerSchema()
    try:
        data = customer_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    new_id = database.insert_customer(data['name'], data['dob'])
    return {'message': 'Successfully inserted with id: {}'.format(new_id)}


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@auth.login_required
def get_customer(customer_id):
    customer = database.get_one_customer(customer_id)
    if customer is None:
        return {'message': 'Customer with id does not exist'}, 404
    else:
        return customer


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@auth.login_required
def update_customer(customer_id):
    json_data = flask.request.get_json()
    if not json_data:
        return {'message': 'No input data'}, 400

    customer_schema = CustomerSchema()
    try:
        data = customer_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422

    # check if id exists
    if not database.check_customer_exists(customer_id):
        return {'message': 'Customer with id does not exist'}, 404

    database.update_customer(customer_id, data['name'], data['dob'])
    return {'message': 'Successfully updated customer with id: {}'.format(customer_id)}


@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@auth.login_required
def delete_customer(customer_id):
    # check if id exists
    if not database.check_customer_exists(customer_id):
        return {'message': 'Customer with id does not exist'}, 404

    database.delete_customer(customer_id)
    return {'message': 'Successfully deleted customer with id: {}'.format(customer_id)}


@app.route('/auth/login', methods=['POST'])
def auth_get_jwt():
    # Note: hard coded user name and password
    # by right the user user name and hashed password should be stored in the backend
    username = 'admin'
    password = 'password'

    json_data = flask.request.get_json()
    if not json_data:
        return {'message': 'No input data'}, 400

    try:
        user_schema = UserSchema()
        data = user_schema.load(json_data)
    except ValidationError as err:
        return {'message': err.messages}, 422

    # check if user and password is the same
    if data['username'] == username and data['password'] == password:
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=2),
                'iat': datetime.datetime.utcnow(),
                'sub': username,
                'admin': True
            }

            return {'token': jwt.encode(payload, SECRET_KEY, algorithm='HS256')}
        except Exception as err:
            return {'message': str(err)}, 500
    else:
        return {'message': "username password combination incorrect"}, 401


app.run()
