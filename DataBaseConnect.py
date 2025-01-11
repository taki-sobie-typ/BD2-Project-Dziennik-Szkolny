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
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establish a connection to the database.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"Connection established for user '{self.user}'.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection = None

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            print(f"Connection for user '{self.user}' closed.")

    def fetch_all_from_view(self, view_name):
        """
        Fetch all records from a specified view, including column headers.
        :param view_name: Name of the database view.
        :return: Tuple (headers, results) where headers is a list of column names, and results is a list of rows.
        """
        if not self.connection:
            raise Exception("Database connection is not established.")

        cursor = self.connection.cursor()
        try:
            query = f"SELECT * FROM {view_name}"  # Query to fetch all rows from the view
            cursor.execute(query)
            results = cursor.fetchall()  # Fetch all results
            headers = [desc[0] for desc in cursor.description]  # Extract column headers
            return headers, results
        except mysql.connector.Error as err:
            print(f"Error executing query on view {view_name}: {err}")
            return [], []
        finally:
            cursor.close()

# Example usage
if __name__ == "__main__":
    # Define credentials for different users
    users = {
        "admin": {"user": "szkolaAdmin", "password": "strongpassword"},
        "teacher": {"user": "nauczyciel", "password": "strongpassword"},
        "parent": {"user": "rodzic", "password": "strongpassword"},
        "student": {"user": "uczen", "password": "strongpassword"},
    }

    # Test connection with each user
    for role, creds in users.items():
        print(f"\nConnecting as {role}...")
        db = DatabaseConnection(user=creds["user"], password=creds["password"])
        db.connect()

        try:
            # Fetch data from a view based on the user's role
            if role == "admin":
                data = db.fetch_all_from_view("lekcje")
            elif role == "teacher":
                data = db.fetch_all_from_view("lekcje_nauczyciela")
            elif role == "parent":
                data = db.fetch_all_from_view("lekcje_rodzica")
            elif role == "student":
                data = db.fetch_all_from_view("lekcje_ucznia")

            print(f"{role.capitalize()} data:")
            for record in data:
                print(record)
        finally:
            db.close()
