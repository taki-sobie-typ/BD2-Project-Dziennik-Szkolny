import tkinter as tk
from DataBaseConnect import DatabaseConnection
from MainScreen import SchoolDiaryApp
from LogInScreen import LoginScreen

class MainApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Dziennik Szkolny")
        self.root.geometry("1200x700")

        # Initialize the menu bar
        self.menu_bar = None

        # Initialize the login screen
        self.login_screen = LoginScreen(self.root, self.db, on_login_success=self.on_login_success)

        # Initialize the main screen
        self.user_data = None
        self.main_screen = SchoolDiaryApp(self.root, self.db, self.user_data)

    def on_login_success(self, user_data):
        """Handle successful login."""
        self.login_screen.hide_login_screen()

        print(user_data.get("imie"))

        # Set user data
        self.user_data = user_data
        user_level = user_data.get('user_level')
        self.main_screen = SchoolDiaryApp(self.root, self.db, self.user_data) #Dodałem bo się user_data nie aktualizował w ocenie (jak ktoś ma lepszy pomysł to zmienić)

        # Update the database connection based on the user level
        if user_level == 3:  # Administrator
            self.db = DatabaseConnection(user="root", password="", host="localhost", database="szkola")
        elif user_level == 2:  # Teacher
            self.db = DatabaseConnection(user="nauczyciel", password="strongpassword", host="localhost", database="szkola")
        elif user_level == 1:  # Parent
            self.db = DatabaseConnection(user="rodzic", password="strongpassword", host="localhost", database="szkola")
        else:  # Student
            self.db = DatabaseConnection(user="uczen", password="strongpassword", host="localhost", database="szkola")

        self.db.connect()  # Establish the new database connection

        # Update the main UI and pass the user data
        self.show_top_ui(user_data)
        self.main_screen.set_user_data(user_data)
        self.main_screen.start()

    def logout(self):
        """Handle logout."""
        # Clear user data
        self.user_data = None
        self.main_screen.hide_main_screen()
        self.hide_top_ui()

        # Close the existing database connection
        if self.db:
            self.db.close()
            self.db = None

        # Reinitialize the database connection for login
        self.db = DatabaseConnection(user="root", password="", host="localhost", database="szkola")
        self.db.connect()

        # Reinitialize the login screen to reset credentials
        self.login_screen = LoginScreen(self.root, self.db, on_login_success=self.on_login_success)

        # Show the new login screen
        self.login_screen.start()
        print("Logged out successfully! Ready for new login.")

    def show_top_ui(self, user_data):
        """Show the top UI with user information."""
        # Ensure any existing menu bar is destroyed before creating a new one
        self.hide_top_ui()

        # Create a new menu bar
        self.menu_bar = tk.Frame(self.root, relief="groove", bd=2, bg="white")
        self.menu_bar.pack(side="top", fill="x")

        # Display logged-in user info
        kto_zalogowany = tk.Label(
            self.menu_bar,
            text=f"KTO ZALOGOWANY: {user_data['imie']} {user_data['nazwisko']}",
            font=("Arial", 10), bg="white"
        )
        kto_zalogowany.pack(side="left", padx=10)

        # Logout button with functionality
        wyloguj = tk.Button(
            self.menu_bar, text="WYLOGUJ", font=("Arial", 10),
            fg="black", bg="white", command=self.logout
        )
        wyloguj.pack(side="right", padx=10)

    def hide_top_ui(self):
        """Hide and destroy the top UI (menu bar)."""
        if self.menu_bar is not None:
            self.menu_bar.destroy()  # Destroy the existing menu bar
            self.menu_bar = None  # Reset the menu_bar reference to None


if __name__ == "__main__":
    # Initial connection for login
    db = DatabaseConnection(user="root", password="", host="localhost", database="szkola")
    db.connect()

    root = tk.Tk()

    # Create the main app instance
    main_app = MainApp(root, db)
    main_app.login_screen.start()

    root.mainloop()

    db.close()  # Close the database connection when the app is closed
