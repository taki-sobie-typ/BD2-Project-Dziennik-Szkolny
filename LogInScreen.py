import tkinter as tk
import bcrypt as bcrypt
from PIL import Image, ImageTk

class LoginScreen:
    def __init__(self, root, db, on_login_success):
        self.root = root
        self.on_login_success = on_login_success  # This function is called on successful login
        self.db = db


    def start(self):
        # Initialize the main login_frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill="both", expand=True)

        self.create_ui()


    def create_ui(self):
        # Create the main container with padding
        container = tk.Frame(self.login_frame, bg="white", padx=30, pady=30)  # Add padding here
        container.pack(padx=50, pady=50, fill="both", expand=True)  # Padding for the entire container

        # School logo at the top of the container
        try:
            image = Image.open("szkola_image.png")
            image = image.resize((130, 65), Image.LANCZOS)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(container, image=logo, bg="white")
            logo_label.pack(pady=10)
            logo_label.image = logo  # Keep reference to the image
        except Exception as e:
            print("Nie można załadować obrazu:", e)

        # Email label and entry
        self.email_label = tk.Label(container, text="Email:", bg="white", font=("Arial", 12), anchor="w")
        self.email_label.pack(pady=5, padx=20, anchor="w")  # Align to the left (west)

        self.email_entry = tk.Entry(container, font=("Arial", 12))
        self.email_entry.pack(pady=5, fill="x", padx=20)

        # Password label and entry
        self.password_label = tk.Label(container, text="Password:", bg="white", font=("Arial", 12), anchor="w")
        self.password_label.pack(pady=5, padx=20, anchor="w")  # Align to the left (west)

        self.password_entry = tk.Entry(container, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5, fill="x", padx=20)

        # Login button
        self.login_button = tk.Button(container, text="Login", font=("Arial", 12), bg="red", command=self.on_login)
        self.login_button.pack(pady=20, padx=20, anchor="w")  # Align to the left (west)

    def on_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Check if the email and password are not empty
        if email and password:
            # Validate user credentials from the database

            # salt = bcrypt.gensalt()
            #hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            #password = hashed_password.decode('utf-8')  # Store as a string
            #print(password)

            user_data = self.db.validate_user(email, password)

            if user_data:
                # If login is successful, pass the necessary user data to the main app
                self.on_login_success(user_data)
            else:
                print("Invalid email or password.")
                # Optionally, show an error message on the UI
        else:
            print("Please enter email and password.")

    def hide_login_screen(self):
        # Clear the email and password entries
        self.email_entry.delete(0, tk.END)  # Clear email input
        self.password_entry.delete(0, tk.END)  # Clear password input

        # Hide the login frame
        self.login_frame.pack_forget()  # Destroy the login screen frame completely

    def show_login_screen(self):
        self.login_frame.pack(fill="both", expand=True)  # Re-show the login screen

