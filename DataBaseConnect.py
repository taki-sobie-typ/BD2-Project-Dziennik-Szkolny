import bcrypt
import mysql.connector

class DatabaseConnection:
    def __init__(self, user, password, host="localhost", database="szkola"):
        """
        Initialize the database connection.
        :param user: The MySQL username.
        :param password: The MySQL user's password.
        :param host: The MySQL server host (default is 'localhost').
        :param database: The MySQL database name.
        """
        self.cursor = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect2(self):
        """Connect to the database."""
        self.connection = mysql.connector.connect(
            user=self.user, password=self.password, host=self.host, database=self.database
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        """Execute a SELECT query and return the results."""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def execute_update(self, query, params=None):
        """Execute an update query (INSERT, UPDATE, DELETE)."""
        self.cursor.execute(query, params or ())
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def connect(self):
        """
        Establish a connection to the database and initialize the cursor.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"Connection established for user '{self.user}'.")
            self.cursor = self.connection.cursor()  # Initialize the cursor after connection
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection = None
            self.cursor = None  # Ensure the cursor is set to None if connection fails

    def close(self):
        """
        Close the database connection and cursor.
        """
        if self.cursor:
            self.cursor.close()  # Close the cursor explicitly
        if self.connection:
            self.connection.close()
            print(f"Connection for user '{self.user}' closed.")

    def fetch_all_from_view(self, view_name):
        """
        Fetch all records from a specified view, including column headers.
        :param view_name: Name of the database view.
        :return: Tuple (headers, results) where headers is a list of column names, and results is a list of rows.
        """
        if not self.connection or not self.cursor:
            raise Exception("Database connection or cursor is not established.")

        try:
            query = f"SELECT * FROM {view_name}"  # Query to fetch all rows from the view
            self.cursor.execute(query)
            results = self.cursor.fetchall()  # Fetch all results
            headers = [desc[0] for desc in self.cursor.description]  # Extract column headers
            return headers, results
        except mysql.connector.Error as err:
            print(f"Error executing query on view {view_name}: {err}")
            return [], []

    def delete_announcements(self, selected_announcements):
        """
        Delete selected announcements from the database.
        :param selected_announcements: A list of announcement IDs to be deleted.
        """

        if not selected_announcements:
            print("No announcements selected for deletion.")
            return

        try:
            placeholders = ", ".join(["%s"] * len(selected_announcements))
            query = f"DELETE FROM ogloszenie WHERE ogloszenie_id IN ({placeholders})"
            self.cursor.execute(query, selected_announcements)
            self.connection.commit()
            print(f"Deleted announcements: {selected_announcements}")
        except mysql.connector.Error as err:
            print(f"Error deleting announcements: {err}")

    def add_announcement(self, title, description, user_data):
        """
        Add a new announcement to the database.
        :param title: Title of the announcement.
        :param description: Description of the announcement.
        """
        if not title or not description.strip():
            print("Title and description cannot be empty.")
            return

        try:
            query = """
                   INSERT INTO ogloszenie (tytul, opis, data_dodania, id_uzytkownik)
                   VALUES (%s, %s, CURDATE(), %s)
                   """
            self.cursor.execute(query, (title, description.strip(), user_data['user_id']))
            self.connection.commit()
            print(f"Added new announcement: {title}")
        except mysql.connector.Error as err:
            print(f"Error adding announcement: {err}")

    def fetch_messages(self, uzytkownik_id, message_type):
        """
        Fetch all messages from a specified view, including column headers.
        :param view_name: Name of the database view (e.g. "messages").
        :return: Tuple (headers, results) where headers is a list of column names, and results is a list of rows.
        """
        if not self.connection or not self.cursor:
            raise Exception("Database connection or cursor is not established.")
        try:
            if message_type == 'received':
            # The modified query to fetch messages along with sender's name and surname
                query = """
                    SELECT 
                        w.data_wiadomosci, 
                        w.temat_wiadomosci, 
                        w.tresc_wiadomosci, 
                        d.imie AS imie_nadawcy, 
                        d.nazwisko AS nazwisko_nadawcy
                    FROM wiadomosc w 
                    LEFT JOIN uzytkownik u ON w.id_uzytkownik_odbierajacy = u.id_uzytkownik
                    LEFT JOIN uczen un ON un.id_uzytkownik = u.id_uzytkownik
                    LEFT JOIN nauczyciel n ON n.id_uzytkownik = u.id_uzytkownik
                    LEFT JOIN administrator a ON a.id_uzytkownik = u.id_uzytkownik
                    LEFT JOIN rodzic r ON r.id_uzytkownik = u.id_uzytkownik
                    LEFT JOIN dane_osobowe d ON d.id_dane_osobowe = un.dane_osobowe_id
                    LEFT JOIN dane_osobowe dn ON dn.id_dane_osobowe = un.dane_osobowe_id
                    LEFT JOIN dane_osobowe da ON da.id_dane_osobowe = un.dane_osobowe_id
                    LEFT JOIN dane_osobowe dr ON dr.id_dane_osobowe = un.dane_osobowe_id
                    WHERE w.id_uzytkownik_wysylajacy = %s
                    ORDER BY w.data_wiadomosci DESC"""
            else:
                query = """
                        SELECT 
                            w.data_wiadomosci, 
                            w.temat_wiadomosci, 
                            w.tresc_wiadomosci, 
                            d.imie AS imie_nadawcy, 
                            d.nazwisko AS nazwisko_nadawcy
                        FROM wiadomosc w 
                        LEFT JOIN uzytkownik u ON w.id_uzytkownik_wysylajacy = u.id_uzytkownik
                        LEFT JOIN uczen un ON un.id_uzytkownik = u.id_uzytkownik
                        LEFT JOIN nauczyciel n ON n.id_uzytkownik = u.id_uzytkownik
                        LEFT JOIN administrator a ON a.id_uzytkownik = u.id_uzytkownik
                        LEFT JOIN rodzic r ON r.id_uzytkownik = u.id_uzytkownik
                        LEFT JOIN dane_osobowe d ON d.id_dane_osobowe = un.dane_osobowe_id
                        LEFT JOIN dane_osobowe dn ON dn.id_dane_osobowe = un.dane_osobowe_id
                        LEFT JOIN dane_osobowe da ON da.id_dane_osobowe = un.dane_osobowe_id
                        LEFT JOIN dane_osobowe dr ON dr.id_dane_osobowe = un.dane_osobowe_id
                        WHERE w.id_uzytkownik_odbierajacy = %s
                        ORDER BY w.data_wiadomosci DESC"""

            self.cursor.execute(query, (uzytkownik_id,))
            results = self.cursor.fetchall()  # Fetch all results
            headers = [desc[0] for desc in self.cursor.description]  # Extract column headers

            return headers, results

        except mysql.connector.Error as err:
            print(f"Error executing query on view: {err}")
            return [], []

    def validate_user(self, email, password):
        """
        Validate user credentials and return user data.
        :param email: The email of the user.
        :param password: The password of the user.
        :return: Dictionary with user data if valid, else None.
        """
        if not self.cursor:
            raise Exception("Cursor is not initialized.")

        validateQuery = """
                SELECT u.id_uzytkownik , u.email, u.haslo , u.id_dane_osobowe, do.imie, do.nazwisko
                FROM uzytkownik u
                JOIN dane_osobowe do ON u.id_dane_osobowe = do.id_dane_osobowe
                WHERE u.email = %s
                """
        self.cursor.execute(validateQuery, (email,))
        result = self.cursor.fetchone()

        if result:
            storedHash = result[2]

            if bcrypt.checkpw(password.encode('utf-8'), storedHash.encode('utf-8')):

                # User data from uzytkownik table
                user_data = {
                    'user_id': result[0],
                    'uczen_id': result[0],
                    'dane_osobowe_id': result[3],
                    'imie': result[4],
                    'nazwisko': result[5]
                }

                # Check for user level (priority: administrator > nauczyciel > rodzic > uczen)
                user_level = -1

                # Check in administrator table
                self.cursor.execute("SELECT 1 FROM administrator WHERE id_uzytkownik = %s", (user_data['user_id'],))
                if self.cursor.fetchone():
                    user_level = 3  # Administrator
                    user_data['user_level'] = user_level
                    # Return user data with the correct user level for administrator
                    return user_data

                # Check in nauczyciel table
                self.cursor.execute("SELECT 1 FROM nauczyciel WHERE id_uzytkownik = %s", (user_data['user_id'],))
                if self.cursor.fetchone():
                    user_level = 2  # Teacher
                    user_data['user_level'] = user_level
                    # Return user data with the correct user level for teacher
                    return user_data

                # Check in rodzic table
                self.cursor.execute("SELECT 1 FROM rodzic WHERE id_uzytkownik = %s", (user_data['user_id'],))
                if self.cursor.fetchone():
                    user_level = 1  # Parent
                    user_data['user_level'] = user_level
                    # Return user data with the correct user level for parent
                    return user_data

                # Check in uczen table
                self.cursor.execute("SELECT 1 FROM uczen WHERE id_uzytkownik = %s", (user_data['user_id'],))
                if self.cursor.fetchone():
                    user_level = 0  # Student
                    user_data['user_level'] = user_level
                    # Return user data with the correct user level for student
                    return user_data

                # If no match found, return None
                return None
        else:
            return None

    def fetch_recipients_from_db(self):
        if not self.connection or not self.cursor:
            raise Exception("Database connection or cursor is not established.")

        try:
            # Kwerendy do pobrania nauczycieli, rodziców, uczniów i administratorów
            queries = {
                'teachers': "SELECT u.id_uzytkownik, ds.imie, ds.nazwisko FROM uzytkownik u LEFT JOIN nauczyciel n ON u.id_uzytkownik = n.id_uzytkownik LEFT JOIN dane_osobowe ds ON n.dane_osobowe_id = ds.id_dane_osobowe",
                'parents': "SELECT u.id_uzytkownik, ds.imie, ds.nazwisko FROM uzytkownik u LEFT JOIN rodzic r ON u.id_uzytkownik = r.id_uzytkownik LEFT JOIN dane_osobowe ds ON r.dane_osobowe_id = ds.id_dane_osobowe",
                'students': "SELECT u.id_uzytkownik, ds.imie, ds.nazwisko, k.nazwa_klasy FROM uzytkownik u LEFT JOIN uczen un ON u.id_uzytkownik = un.id_uzytkownik LEFT JOIN dane_osobowe ds ON un.dane_osobowe_id = ds.id_dane_osobowe LEFT JOIN klasa k ON un.klasa_id = k.klasa_id",
                'admins': "SELECT u.id_uzytkownik, ds.imie, ds.nazwisko FROM uzytkownik u LEFT JOIN administrator a ON u.id_uzytkownik = a.id_uzytkownik LEFT JOIN dane_osobowe ds ON a.dane_osobowe_id = ds.id_dane_osobowe"
            }

            # Wykonanie zapytań i połączenie wyników
            all_users = []

            # Nauczyciele
            self.cursor.execute(queries['teachers'])
            teachers = self.cursor.fetchall()
            for teacher in teachers:
                all_users.append({
                    'id_uzytkownika': teacher[0],
                    'imie': teacher[1],
                    'nazwisko': teacher[2],
                    'typ': 'nauczyciel'
                })

            # Rodzice
            self.cursor.execute(queries['parents'])
            parents = self.cursor.fetchall()
            for parent in parents:
                all_users.append({
                    'id_uzytkownika': parent[0],
                    'imie': parent[1],
                    'nazwisko': parent[2],
                    'typ': 'rodzic'
                })

            # Uczniowie
            self.cursor.execute(queries['students'])
            students = self.cursor.fetchall()
            for student in students:
                all_users.append({
                    'id_uzytkownika': student[0],
                    'imie': student[1],
                    'nazwisko': student[2],
                    'klasa': student[3],  # Klasa ucznia
                    'typ': 'uczen'
                })

            # Administratorzy
            self.cursor.execute(queries['admins'])
            admins = self.cursor.fetchall()
            for admin in admins:
                all_users.append({
                    'id_uzytkownika': admin[0],
                    'imie': admin[1],
                    'nazwisko': admin[2],
                    'typ': 'administrator'
                })

            return all_users

        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return []

    def send_messages(self, title, description, selected_ids, user_data):
        """
        Sends a message to the selected recipients and stores the message in the database.
        This function will send individual messages to each recipient.
        :param title: The title of the message.
        :param description: The description (body) of the message.
        :param selected_ids: A list of recipient IDs.
        :param user_data: Information about the user sending the message (e.g., user_id).
        :return: None
        """
        if not self.connection or not self.cursor:
            raise Exception("Database connection or cursor is not established.")

        try:
            # Get the current timestamp for the message date
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Iterate over selected recipient IDs and send messages one by one
            for recipient_id in selected_ids:
                # Insert the message into the messages table (one message per recipient)
                insert_message_query = """
                    INSERT INTO wiadomosc (data_wiadomosci, id_uzytkownik_wysylajacy, id_uzytkownik_odbierajacy, temat_wiadomosci, tresc_wiadomosci)
                    VALUES (CURDATE(), %s, %s, %s, %s)
                """
                # Insert the message into the database
                self.cursor.execute(insert_message_query,
                                    (recipient_id,  # recipient_id goes here
                                     user_data,  # user_id goes here (sender)
                                     title,  # title of the message
                                     description))  # description (body of the message)
                self.connection.commit()

            print(f"Message sent to {len(selected_ids)} recipients.")

        except mysql.connector.Error as err:
            print(f"Error sending message: {err}")
            self.connection.rollback()  # Rollback in case of an error
