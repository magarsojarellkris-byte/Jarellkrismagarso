from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to my first API!"


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00138",
        "name": "Jarell Kris Magarso",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })

@app.route('/food')
def get_food():
    return jsonify({
        "food_name": "Chicken Adobo",
        "category": "Main Dish",
        "price": 85,
        "available": True
    })

@app.route('/multiply')
def multiply_numbers():
    num1 = request.args.get('num1', type=float)
    num2 = request.args.get('num2', type=float)

    if num1 is None or num2 is None:
        return jsonify({
            "error": "Please provide num1 and num2."
        }), 400

    return jsonify({
        "number1": num1,
        "number2": num2,
        "result": num1 * num2
    })


if __name__ == '__main__':
    app.run(debug=True)