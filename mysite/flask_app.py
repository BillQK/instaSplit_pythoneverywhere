# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/hello", methods=["GET"])

def hello():

    return jsonify({"message": "Hello, World! from Nick :^)"})

@app.route("/api/getProducts", methods=["GET"])

def getProducts():

    # Get the value of the 'category' parameter from the request query string

    category = request.args.get('category')

    # Use the 'category' parameter in the response message

    if category:

        message = f"Products in category: {category}"

    else:

        message = "No category specified for products"

    return jsonify({"message": message})

if __name__ == "__main__":

    app.run(debug=True)
