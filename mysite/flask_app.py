from flask import Flask, request, jsonify

app = Flask(__name__)

# Initial mock data structure
app_data = {
    "users" : [
         {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-555-5555",
                    "password": 123,
                    "balance": -300,
                }]
    "groups": {
        "apartment": {
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
                {"id": 1,
                    "who_pay?": "Jane Doe",
                    "description": "March cleaning supply",
                    "amt": 100
                },
                {"id": 2,
                    "who_pay?": "Jane Doe",
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
                    "id": 1,
                    "who_pay?": "Jane Doe",
                    "description": "March cleaning supply",
                    "amt": 100
                },
                {
                    "id": 2,
                    "who_pay?": "Jane Doe",
                    "description": "April utility bill",
                    "amt": 200
                }
            ],
        },

    }
}


@app.route("/api/users/register", methods=["POST"])  # Changed to POST to align with common practices
def register_user():
    data = request.json
    if data:
        email = data.get('email')
        if any(user['email'] == email for user in app_data['users']):
            return jsonify({"message": "Email already exists"}), 409

        new_user = {
            "email": email,
            "phone": data.get('phoneNumber'),
            "password": generate_password_hash(data.get('password')),
            "name": data.get('username'),
            "balance": 0  # Assuming you want to track balance
        }
        app_data['users'].append(new_user)
        return jsonify(new_user), 201
    else:
        return jsonify({"message": "Invalid data"}), 400


@app.route("/api/users/login", methods=["POST"])
def login_user():
    data = request.json
    if data:
        email = data.get('email')
        password = data.get('password')
        user = next((user for user in app_data['users'] if user['email'] == email), None)
        if user and check_password_hash(user['password'], password):
            return jsonify({"message": "Login successful", "user": user['name']}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    else:
        return jsonify({"message": "Invalid login data"}), 400





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

@app.route("/api/groups/<group_name>/members/<member_email>", methods=["DELETE"])
def remove_member(group_name, member_email):
    group = app_data['groups'].get(group_name)
    if group:
        members = group['members']
        original_len = len(members)
        group['members'] = [member for member in members if member['email'] != member_email]
        if len(group['members']) < original_len:
            return jsonify({"message": f"Member with email {member_email} removed from group '{group_name}'"}), 200
        else:
            return jsonify({"message": "Member not found"}), 404
    else:
        return jsonify({"message": "Group not found"}), 404

@app.route("/api/groups/<group_name>/expenses/<expense_id>", methods=["DELETE"])
def remove_expense(group_name, expense_id):
    group = app_data['groups'].get(group_name)
    if group:
        expenses = group['expenses']
        original_len = len(expenses)
        group['expenses'] = [expense for expense in expenses if str(expense['id']) != expense_id]
        if len(group['expenses']) < original_len:
            return jsonify({"message": f"Expense with id {expense_id} removed from group '{group_name}'"}), 200
        else:
            return jsonify({"message": "Expense not found"}), 404
    else:
        return jsonify({"message": "Group not found"}), 404

@app.route("/api/groups/<group_name>", methods=["DELETE"])
def delete_group(group_name):
    if group_name in app_data['groups']:
        del app_data['groups'][group_name]
        return jsonify({"message": f"Group '{group_name}' deleted successfully"}), 200
    else:
        return jsonify({"message": "Group not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
