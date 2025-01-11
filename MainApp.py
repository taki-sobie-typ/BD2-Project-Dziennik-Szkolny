import tkinter as tk
from DataBaseConnect import DatabaseConnection
from MainScreen import SchoolDiaryApp
from LogInScreen import LoginScreen

def start_main_app(root, db, user_data):
    # This function starts the main app after successful login with the current user data
    app = SchoolDiaryApp(root, db, user_data)
    root.mainloop()

class MainApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Dziennik Szkolny")
        self.root.geometry("1200x700")

        # Start the login screen
        self.login_screen = LoginScreen(self.root, self.db, on_login_success=self.on_login_success)

    def on_login_success(self, user_data):
        # Pass the user data to the main app after successful login
        self.login_screen.hide_login_screen()

        # Set the correct database connection and user level based on user_data
        user_level = user_data.get('user_level')

        if user_level == 3:  # Administrator
            self.db = DatabaseConnection(user="szkolaAdmin", password="strongpassword", host="localhost", database="szkola")
        elif user_level == 2:  # Teacher
            self.db = DatabaseConnection(user="nauczyciel", password="strongpassword", host="localhost", database="szkola")
        elif user_level == 1:  # Parent
            self.db = DatabaseConnection(user="rodzic", password="strongpassword", host="localhost", database="szkola")
        else:  # Student
            self.db = DatabaseConnection(user="uczen", password="strongpassword", host="localhost", database="szkola")

        self.db.connect()  # Establish the connection for the current user level

        # Start the main app with the user data
        start_main_app(self.root, self.db, user_data)

if __name__ == "__main__":
    # Initial connection with root user for login purpose (this might be replaced later)
    db = DatabaseConnection(user="root", password="", host="localhost", database="szkola")
    db.connect()

    root = tk.Tk()

    # Create MainApp instance, which starts the login screen
    main_app = MainApp(root, db)

    root.mainloop()

    db.close()  # Close the database connection when the app is closed
