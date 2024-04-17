from flask import Flask, request, jsonify

app = Flask(__name__)


DEFAULT_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1jVxHEjBZkIfrz6bYmOy1cE-pbs6Hpdb324HOb2Ntlg&s"
TRAVEL_GROUP_IMAGE_URL = "https://thumb.ac-illust.com/23/23ae0414df316a166952315cbf00cdd9_t.jpeg"
APT_GROUP_IMAGE_URL = "https://www.creativefabrica.com/wp-content/uploads/2022/04/22/Apartment-for-rent-Graphics-29438801-1-580x387.jpg"
MEMBER_IMAGE_1 = "https://avatar.iran.liara.run/public/1" #John Doe?
MEMBER_IMAGE_2 = "https://avatar.iran.liara.run/public/41"
MEMBER_IMAGE_3 = "https://avatar.iran.liara.run/public/87" #Jane Doe?
CLEANING_SUPPLY = "https://static.vecteezy.com/system/resources/thumbnails/009/677/869/small/bucket-with-cleaning-supplies-collection-isolated-on-white-background-housework-concept-design-elements-illustration-vector.jpg"
UTILITY_BILL = "https://cdn-icons-png.flaticon.com/512/7866/7866488.png"
LUNCH = "https://cdn-icons-png.freepik.com/256/2771/2771406.png"
UBER = "https://cdn-icons-png.flaticon.com/512/2077/2077143.png"

# Initial mock data structure
app_data = {
    "groups": {
        "apartment": {
            "image": APT_GROUP_IMAGE_URL,
            "members": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": -300,
                    "image": MEMBER_IMAGE_1
                },
                {
                    "name": "Jane Doe",
                    "email": "jane.doe@example.com",
                    "phone": "555-555-5556",
                    "balance": 300,
                    "image": MEMBER_IMAGE_3
                },
            ],
            "expenses": [
                {
                    "who_pay?": "Jane Doe",
                    "description": "March cleaning supply",
                    "amt": 100,
                    "image": CLEANING_SUPPLY
                },
                {
                    "who_pay?": "Jane Doe",
                    "description": "April utility bill",
                    "amt": 200,
                    "image": UTILITY_BILL
                }
            ],
        },
        "Coop Group": {
            "image": TRAVEL_GROUP_IMAGE_URL,
            "members": [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "555-555-5555",
                    "balance": -300,
                    "image": MEMBER_IMAGE_1
                },
                {
                    "name": "Bob Smith",
                    "email": "bob.smith@example.com",
                    "phone": "555-555-5557",
                    "balance": 300,
                    "image": MEMBER_IMAGE_2
                },
            ],
            "expenses": [
                {
                    "who_pay?": "Bob Smith",
                    "description": "March 22 lunch",
                    "amt": 100,
                    "image": LUNCH
                },
                {
                    "who_pay?": "Bob Smith",
                    "description": "Uber to airport",
                    "amt": 200,
                    "image": UBER
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
