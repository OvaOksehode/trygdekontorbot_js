import sqlite3
import os

from datetime import datetime


def print_all_entries(con, table):
    """Skriv ut alle oppføringer fra en gitt tabell."""
    try:
        with con:
            cursor = con.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print(f"Ingen oppføringer funnet i tabellen '{table}'.")
    except sqlite3.Error as e:
        print(f"Feil ved henting av data fra tabellen '{table}': {e}")

def connect_to_database(db_name):
    """Koble til SQLite-databasen og returner forbindelsen."""
    if os.path.exists(db_name):
        try:
            con = sqlite3.connect(db_name)
            print(f"Koblet til databasen '{db_name}'.")
            return con
        except sqlite3.Error as e:
            print(f"Feil ved tilkobling til databasen: {e}")
            return None
    else:
        print(f"Kunne ikke finne databasen '{db_name}'.")
        return None

def get_company_balance(con, owner_id):
    """Hent saldoen for ett selskap fra 'Company'-tabellen og returner det som en int."""
    try:
        with con:
            cursor = con.cursor()
            cursor.execute("SELECT balance FROM Company WHERE owner_id = ?", (owner_id,))
            row = cursor.fetchone()
            if row:
                # Returner saldoen som en int
                return int(row[0])
            else:
                # Ingen selskap funnet med gitt owner_id
                return None  # Eller en annen passende verdi for å indikere at selskapet ikke ble funnet
    except sqlite3.Error as e:
        print(f"Feil ved henting av saldo: {e}")
        return None  # Eller en annen passende verdi for å indikere at det oppstod en feil

def get_all_users(con):
    data = {}
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Company")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                data[row[0]] = {
                    "owner_id": row[0],
                    "name": row[1],
                    "balance": row[2]
                }
        else:
            print("Ingen oppføringer funnet i tabellen 'Company'.")
    except sqlite3.Error as e:
        print(f"Feil ved henting av data fra tabellen 'Company': {e}")
    return data

def delete_company_entry(con, company_owner_id):
    """Slett en oppføring fra 'Company'-tabellen basert på company_id."""
    try:
        with con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM Company WHERE owner_id = ?", (company_owner_id,))
            if cursor.rowcount > 0:
                print(f"Slettet oppføringen med owner_id {company_owner_id} fra 'Company'-tabellen.")
                return True
            else:
                print(f"Ingen oppføring funnet med owner_id {company_owner_id}.")
                return False
    except sqlite3.Error as e:
        print(f"Feil ved sletting av oppføring fra 'Company'-tabellen: {e}")

def create_company(con, owner_id, name=None, balance=None):
    # Bruker standardverdier hvis ingen verdier er oppgitt
    if name is None:
        name = "Unknown Company"
    if balance is None:
        balance = 0.0
    
    try:
        # Sett inn i databasen
        with con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO Company (owner_id, name, balance) VALUES (?, ?, ?)",
                (owner_id, name, balance)
            )
            print(f"Selskapet {name} ble opprettet og satt inn i databasen.")
    except sqlite3.Error as e:
        print(f"Feil ved innsending til databasen: {e}")

    return True

def create_transaction(con, sender_owner_id, receiver_owner_id, amount):
    try:
        with con:
            cursor = con.cursor()

            # Hent saldo for sender
            cursor.execute("SELECT balance FROM Company WHERE owner_id = ?", (sender_owner_id,))
            sender_balance = cursor.fetchone()
            if sender_balance is None:
                print(f"Sender med ID {sender_owner_id} ble ikke funnet.")
                return None

            sender_balance = sender_balance[0]

            # Sjekk om sender har nok penger
            if sender_balance < amount:
                print("Sender har ikke nok penger.")
                return None

            # Hent saldo for mottaker
            cursor.execute("SELECT balance FROM Company WHERE owner_id = ?", (receiver_owner_id,))
            receiver_balance = cursor.fetchone()
            if receiver_balance is None:
                print(f"Mottaker med ID {receiver_owner_id} ble ikke funnet.")
                return None

            receiver_balance = receiver_balance[0]

            # Oppdater saldoene
            new_sender_balance = sender_balance - amount
            new_receiver_balance = receiver_balance + amount

            # Oppdater senderens saldo
            cursor.execute("UPDATE Company SET balance = ? WHERE owner_id = ?", (new_sender_balance, sender_owner_id))

            # Oppdater mottakerens saldo
            cursor.execute("UPDATE Company SET balance = ? WHERE owner_id = ?", (new_receiver_balance, receiver_owner_id))

            # Få nåværende dato og tid som Unix-tidsstempel
            unix_timestamp = datetime.now().timestamp()

            # Sett inn transaksjonen i C_Transaction-tabellen
            cursor.execute("""
                INSERT INTO C_Transaction (sender_id, receiver_id, amount, date)
                VALUES (?, ?, ?, ?)
            """, (sender_owner_id, receiver_owner_id, amount, unix_timestamp))
            
            # Få den siste innsatte transaction_id
            transaction_id = cursor.lastrowid

            print(f"Ny transaksjon opprettet med ID {transaction_id}.")

            return transaction_id
    except sqlite3.Error as e:
        print(f"Feil ved opprettelse av transaksjon: {e}")
        return None

def rename_company(con, company_id, new_name):
    """Endre navnet på et selskap i 'Company'-tabellen basert på company_id."""
    try:
        with con:
            cursor = con.cursor()
            cursor.execute("UPDATE Company SET name = ? WHERE owner_id = ?", (new_name, company_id))
            if cursor.rowcount > 0:
                print(f"Navnet på selskapet med owner_id {company_id} ble oppdatert til '{new_name}'.")
                return True
            else:
                print(f"Ingen oppføring funnet med owner_id {company_id}.")
                return False
    except sqlite3.Error as e:
        print(f"Feil ved oppdatering av selskapets navn: {e}")
        return False


def main():
    database_name = "janovecoin.db"
    con = connect_to_database(database_name)

    if con:
        #print_all_entries(con, "C_Transaction")
        create_transaction(con, sender_owner_id=1, receiver_owner_id=2, amount=100.0)
        con.close()

if __name__ == "__main__":
    main()
