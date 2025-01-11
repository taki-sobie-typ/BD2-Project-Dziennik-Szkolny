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

    def validate_user(self, email, password):
        """
        Validate user credentials and return user data.
        :param email: The email of the user.
        :param password: The password of the user.
        :return: Dictionary with user data if valid, else None.
        """
        if not self.cursor:
            raise Exception("Cursor is not initialized.")

        query = """
                SELECT u.id_uzytkownik , u.email, u.haslo , uc.uczen_id, uc.dane_osobowe_id, do.imie, do.nazwisko
                FROM uzytkownik u
                JOIN uczen uc ON u.id_uzytkownik = uc.uczen_id
                JOIN dane_osobowe do ON uc.dane_osobowe_id = do.id_dane_osobowe
                WHERE u.email = %s AND u.haslo = %s
                """
        self.cursor.execute(query, (email, password))
        result = self.cursor.fetchone()

        if result:
            # User data from uzytkownik table
            user_data = {
                'user_id': result[0],
                'uczen_id': result[3],
                'dane_osobowe_id': result[4],
                'imie': result[5],
                'nazwisko': result[6]
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
