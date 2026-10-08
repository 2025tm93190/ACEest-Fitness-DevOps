from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample member data
members = [
    {
        "id": 1,
        "name": "John",
        "age": 25,
        "membership": "Premium"
    },
    {
        "id": 2,
        "name": "Sarah",
        "age": 30,
        "membership": "Basic"
    }
]


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to ACEest Fitness & Gym",
        "status": "Application is running"
    })


@app.route("/members", methods=["GET"])
def get_members():
    return jsonify(members)


@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    return jsonify(member)


@app.route("/members", methods=["POST"])
def add_member():
    data = request.get_json()

    if not data or "name" not in data or "age" not in data:
        return jsonify({
            "error": "Name and age are required"
        }), 400

    new_member = {
        "id": len(members) + 1,
        "name": data["name"],
        "age": data["age"],
        "membership": data.get("membership", "Basic")
    }

    members.append(new_member)

    return jsonify(new_member), 201


@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    members.remove(member)

    return jsonify({
        "message": "Member deleted successfully"
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)