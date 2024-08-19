from flask import Flask, request, jsonify
import sqlite3
from database_functions import get_all_users, delete_company_entry, create_company, create_transaction, get_company_balance, rename_company

app = Flask(__name__)

def get_db_connection():
    con = sqlite3.connect("janovecoin.db")
    con.row_factory = sqlite3.Row  # Optional: Makes rows behave like dictionaries
    return con

@app.route("/")
def home():
    return "Trygdekontorbot API ver 0.0"

@app.route("/getallusers")
def get_users():
    con = get_db_connection()
    users = get_all_users(con)
    con.close()
    return jsonify(users)

@app.route("/createcompany/<int:owner_id>", methods=["POST"])
def create_company_route(owner_id):
    name = request.args.get('name', None)  # Hent 'name' fra query-parametere, None hvis ikke gitt
    balance = request.args.get('balance', None)  # Hent 'balance' fra query-parametere, None hvis ikke gitt

    # Hvis balance er gitt som streng, må vi konvertere det til float
    if balance is not None:
        try:
            balance = float(balance)
        except ValueError:
            return jsonify({"error": "Balance må være et gyldig tall."}), 400

    con = get_db_connection()
    company = create_company(con, owner_id, name, balance)
    con.close()

    return jsonify({
        "message": f"Company '{name}' created successfully.",
        "company": {
            "owner_id": owner_id,
            "name": name,
            "balance": balance
        }
    })

@app.route("/deletecompany/<int:company_id>", methods=["DELETE"])
def delete_company(company_id):
    con = get_db_connection()
    delete_company_entry(con, company_id)
    con.close()
    return jsonify({"message": f"Company with owner_id {company_id} deleted."})

@app.route("/create_transaction", methods=["POST"])
def create_transaction_route():
    try:
        # Hent data fra forespørselen
        data = request.get_json()

        sender_owner_id = data.get("sender_owner_id")
        amount = data.get("amount")

        # Valider at de nødvendige parametrene er inkludert
        if sender_owner_id is None or amount is None:
            return jsonify({"error": "sender_owner_id and amount are required"}), 400

        # Mottaker kan være en av følgende: receiver_user (en Discord-bruker) eller receiver_name (selskapets navn)
        receiver_user = data.get("receiver_user")
        receiver_name = data.get("receiver_name")

        if not receiver_user and not receiver_name:
            return jsonify({"error": "One of receiver_user or receiver_name must be provided."}), 400

        # Opprett en databaseforbindelse
        con = get_db_connection()
        cursor = con.cursor()

        # Finn mottaker basert på angitte kriterier
        if receiver_user:
            cursor.execute("SELECT owner_id FROM Company WHERE owner_id = ?", (receiver_user["user_id"],))
        elif receiver_name:
            cursor.execute("SELECT owner_id FROM Company WHERE name = ?", (receiver_name,))

        receiver_data = cursor.fetchone()
        
        if receiver_data is None:
            return jsonify({"error": "Receiver not found."}), 404

        receiver_owner_id = receiver_data[0]  # Hent owner_id til mottakeren

        # Kall create_transaction-funksjonen
        transaction_id = create_transaction(con, sender_owner_id, receiver_owner_id, amount)

        # Lukk forbindelsen
        con.close()

        # Returner resultatet som JSON
        if transaction_id:
            return jsonify({"success": True, "transaction_id": transaction_id}), 201
        else:
            return jsonify({"success": False, "error": "Failed to create transaction"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/rename_company", methods=["POST"])
def rename_company_route():
    # Hent data fra POST-forespørselen
    data = request.get_json()
    
    if not data or "company_id" not in data or "new_name" not in data:
        return jsonify({"error": "company_id and new_name are required."}), 400
    
    company_id = data["company_id"]
    new_name = data["new_name"]

    # Koble til databasen
    con = get_db_connection()
    
    # Endre navnet på selskapet
    success = rename_company(con, company_id, new_name)
    
    con.close()
    
    if success:
        return jsonify({"message": f"Company with owner_id {company_id} was renamed to '{new_name}'."}), 200
    else:
        return jsonify({"error": "Failed to rename company. Make sure the company exists."}), 404

@app.route("/get_balance/<int:owner_id>", methods=["GET"])
def get_balance_route(owner_id):
    # """Flask-rute som returnerer saldoen for et selskap basert på owner_id."""
    con = get_db_connection()
    balance = get_company_balance(con, owner_id)
    con.close()

    if balance is not None:
        return jsonify({"owner_id": owner_id, "balance": balance}), 200
    else:
        return jsonify({"error": "Ingen selskap funnet med gitt owner_id."}), 404

if __name__ == "__main__":
    app.run(debug=True)
