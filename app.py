from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# ------------------ GLOBAL VARIABLES ------------------
HISTORY_FILE = "history.txt"
memory = 0
last_result = 0

# ------------------ FUNCTIONS ------------------
def save_to_history(equation, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, 'a') as file:
        file.write(f"{timestamp} | {equation} = {result}\n")

def get_history():
    try:
        lines = list(reversed([line.strip() for line in open(HISTORY_FILE).readlines()]))
        # Return numbered strings directly
        return [f"{i+1}. {line}" for i, line in enumerate(lines)]
    except FileNotFoundError:
        return []

def clear_history():
    open(HISTORY_FILE, 'w').close()

def delete_last_history():
    try:
        lines = open(HISTORY_FILE).readlines()
        if lines:
            removed = lines.pop()
            open(HISTORY_FILE, 'w').writelines(lines)
            return removed.strip()
        return None
    except FileNotFoundError:
        return None

def calculate_expression(user_input):
    global last_result
    parts = user_input.split()
    if len(parts) != 3:
        return {"error": "Use format: number operator number (e.g., 7 + 3)"}

    try:
        num1 = float(parts[0])
        op = parts[1]
        num2 = float(parts[2])
    except ValueError:
        return {"error": "Invalid numbers"}

    if op == "+":
        result = num1 + num2
    elif op == "-":
        result = num1 - num2
    elif op == "*":
        result = num1 * num2
    elif op == "/":
        if num2 == 0:
            return {"error": "Cannot divide by 0"}
        result = num1 / num2
    else:
        return {"error": "Invalid operator"}

    if result.is_integer():
        result = int(result)

    last_result = result
    save_to_history(f"{num1} {op} {num2}", result)
    return {"result": result}

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_api():
    expression = request.form.get("expression", "")
    return jsonify(calculate_expression(expression))

@app.route("/history", methods=["GET"])
def history_api():
    return jsonify({"history": get_history()})

@app.route("/history/undo", methods=["POST"])
def undo_api():
    removed = delete_last_history()
    return jsonify({"message": "Last history removed" if removed else "No history to delete",
                    "text": removed or ""})

@app.route("/history/clear", methods=["POST"])
def clear_api():
    clear_history()
    return jsonify({"message": "History cleared"})

# ------------------ MEMORY ------------------
@app.route("/memory/add", methods=["POST"])
def memory_add():
    global memory, last_result
    memory += last_result
    return jsonify({"memory": memory})

@app.route("/memory/subtract", methods=["POST"])
def memory_subtract():
    global memory, last_result
    memory -= last_result
    return jsonify({"memory": memory})

@app.route("/memory/recall", methods=["GET"])
def memory_recall():
    return jsonify({"memory": memory})

@app.route("/memory/clear", methods=["POST"])
def memory_clear():
    global memory
    memory = 0
    return jsonify({"memory": memory})

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(debug=True)
