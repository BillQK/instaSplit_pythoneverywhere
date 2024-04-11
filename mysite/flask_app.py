from flask import Flask, request, jsonify

app = Flask(__name__)

# Initial mock data structure
app_data = {
    "groups": {
        "apartment": {
            "members": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": 0.0,
                },
                {
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": 0.0,
                },
            ],
            "expenses": [
                {
                    "description": "March cleaning supply",
                    "amt": 100
                },
                {
                    "description": "April utility bill",
                    "amt": 200
                }
            ],
        },
        "Coop Group": {
            "members": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": -300,
                },
                {
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": 300,
                },
            ],
            "expenses": [
                {
                    "who_pay?": "Jane Doe",
                    "description": "March cleaning supply",
                    "amt": 100
                },
                {
                    "who_pay?": "Jane Doe",
                    "description": "April utility bill",
                    "amt": 200
                }
            ],
        },

    }
}


@app.route("/api/groups/<group_name>", methods=["GET"])
def get_group(group_name):
    group = app_data['groups'].get(group_name)
    if group:
        return jsonify(group), 200
    else:
        return jsonify({"message": "Group not found"}), 404

@app.route("/api/groups/<group_name>", methods=["PUT"])
def edit_group(group_name):
    updated_data = request.json
    if group_name in app_data['groups'] and updated_data:
        app_data['groups'][group_name].update(updated_data)
        return jsonify({"message": f"Group '{group_name}' updated successfully"}), 200
    else:
        return jsonify({"message": "Group not found or invalid data"}), 400

@app.route("/api/groups/<group_name>/expenses", methods=["GET"])
def get_expenses(group_name):
    group = app_data['groups'].get(group_name)
    if group:
        return jsonify(group['expenses']), 200
    else:
        return jsonify({"message": "Group not found"}), 404

@app.route("/api/groups", methods=["POST"])
def create_group():
    group_name = request.json.get('name')
    if group_name:
        app_data['groups'][group_name] = {"members": [], "expenses": []}
        return jsonify({"message": f"Group '{group_name}' created successfully"}), 201
    else:
        return jsonify({"message": "Group name is required"}), 400

@app.route("/api/groups/<group_name>/members", methods=["POST"])
def add_member(group_name):
    member_data = request.json
    if group_name in app_data['groups'] and member_data:
        app_data['groups'][group_name]["members"].append(member_data)
        return jsonify({"message": f"Member added to group '{group_name}'"}), 201
    else:
        return jsonify({"message": "Group does not exist or member data is invalid"}), 400

@app.route("/api/groups/<group_name>/expenses", methods=["POST"])
def add_expense(group_name):
    expense_data = request.json
    if group_name in app_data['groups'] and expense_data:
        description = expense_data.get('description', '')
        amount = float(expense_data.get('amt', 0))

        group = app_data['groups'][group_name]
        members = group["members"]
        num_members = len(members)

        if num_members > 0 and amount > 0:
            split_amount = amount / num_members
            for member in members:
                member['balance'] -= split_amount  # Assuming the member owes this amount

            group["expenses"].append({"description": description, "amt": amount, "split_amount": split_amount})
            return jsonify({"message": f"Expense '{description}' added and split in group '{group_name}'", "expense_data": expense_data}), 201
        else:
            return jsonify({"message": "No members in group to split the expense or invalid amount"}), 400
    else:
        return jsonify({"message": "Group does not exist or expense data is invalid"}), 400


if __name__ == "__main__":
    app.run(debug=True)
