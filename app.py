import config
from flask import Flask, render_template, request, jsonify
from binance.client import Client
from binance.enums import *
app = Flask(__name__)
data = {}
orders= []
api_url = config.API_URL
api_key = config.API_KEY
api_secret = config.API_SECRET
client = Client(api_key, api_secret)
 
# set up flag to check if script has run before
has_run_before = False

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f'Received webhook with data: {request.json}')
    global data, has_run_before
    data = request.json
    order = None
    # get the previous market position only if script has run before
    if has_run_before:
        prev_market_position = data["strategy"]["prev_market_position"]
        size = float(data["strategy"]["prev_market_position_size"])
    else:
        prev_market_position = None
        size = None    
    symbol = "BTCUSDT"
    type="ORDER_TYPE_LIMIT"
    quantity = float(data["strategy"]["market_position_size"])
    side = data["strategy"]["order_action"].upper()
    price = data["strategy"]["order_price"]
    time_in_force="TIME_IN_FORCE_GTC"

    print(side, size, quantity, price)
    # create a sell order to close the position if previous position exists
    if prev_market_position is not None:
        if prev_market_position == "long":
            order = client.create_order(
            symbol = symbol,
            side = side,
            type = type,
            timeInForce = time_in_force,
            quantity = quantity,
            price = price
        )
            if  order:
                print("Closed previous order sell successfully:")
                print(order)
                orders.append(order)
            else:
                print("Failed to close previous sell order:")
                print(order)            

        elif prev_market_position == "short":
            order = client.create_order(
            symbol = symbol,
            side = side,
            type = type,
            timeInForce = time_in_force,
            quantity = quantity,
            price = price
        )
            if  order:
                print("Closed previous buy order successfully:")
                print(order)
                orders.append(order)
            else:
                print("Failed to close previous buy order:")
                print(order)

    # place a new order
    if data["strategy"]["order_action"] == "buy":
            order = client.create_order(
            symbol = symbol,
            side = side,
            type = type,
            timeInForce = time_in_force,
            quantity = quantity,
            price = price         
        )
            if  order:
                print("New buy order placed successfully:")
                print(order)
                orders.append(order)
            else:
                print("Failed to place new buy order:")
                print(order) 
    elif data["strategy"]["order_action"] == "sell":
            order = client.create_order(
            symbol = symbol,
            side = side,
            type = type,
            timeInForce = time_in_force,
            quantity = quantity,
            price = price
        )
    if  order:
        print("New sell order placed successfully:")
        print(order)
        orders.append(order)
    else:
        print("Failed to place new sell order:")
        print(order)

    # update flag to indicate script has run before

    has_run_before = True

    return jsonify({'message': 'Success'}), 200

@app.route('/data')
def get_data():
    return jsonify(data)
@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify({'orders': orders})
@app.route('/')
def index():
    return render_template('index.ejs', data=data)
if __name__ == "__main__":
    app.run(port=8080)    