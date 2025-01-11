import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class SchoolDiaryApp:
    def __init__(self, root, db_connection, user_data):
        self.root = root
        self.db = db_connection
        self.user_data = user_data  # Store the user data

        self.root.title("Dziennik szkolny")
        self.root.geometry("1200x700")
        self.root.config(bg="lightgray")
        self.root.resizable(False, False)

        self.current_frame = None  # To track the currently displayed content
        self.create_ui()

    def create_ui(self):
        # Górny pasek menu
        menu_bar = tk.Frame(self.root, relief="groove", bd=2, bg="white")
        menu_bar.pack(side="top", fill="x")

        # Display logged-in user info
        kto_zalogowany = tk.Label(menu_bar, text=f"KTO ZALOGOWANY: {self.user_data['imie']} {self.user_data['nazwisko']}",
                                  font=("Arial", 10), bg="white")
        kto_zalogowany.pack(side="left", padx=10)

        wyloguj = tk.Button(menu_bar, text="WYLOGUJ", font=("Arial", 10), fg="black", bg="white")
        wyloguj.pack(side="right", padx=10)

        # Toolbar
        self.toolbar = tk.Frame(self.root, relief="raised", bd=2, bg="white")
        self.toolbar.pack(side="top", fill="x", pady=5, padx=10)

        self.icons = {
            "\u2709": "messages",
            "\U0001f393": "lessons",
            "\U0001f514": "notifications",
            "\U0001f4c5": "calendar",
            "\u26a0": "warnings",
            "\U0001f465": "students"
        }
        for icon, view in self.icons.items():
            button = tk.Button(
                self.toolbar, text=icon, font=("Arial", 14), width=6, height=3,
                fg="black", bg="white", command=lambda v=view: self.switch_view(v)
            )
            button.pack(side="left", padx=10, pady=5)

        # Add school logo
        try:
            image = Image.open("szkola_image.png")
            image = image.resize((130, 65), Image.LANCZOS)
            logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(self.toolbar, image=logo, bg="white")
            logo_label.pack(side="right", padx=10)
            logo_label.image = logo
        except Exception as e:
            print("Nie można załadować obrazu:", e)

        # Scrollable main container
        self.main_container = tk.Frame(self.root, bg="white")
        self.main_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Footer
        footer_frame = tk.Frame(self.root, bg="white", height=20)
        footer_frame.pack(side="bottom", fill="x")

        footer_label = tk.Label(
            footer_frame,
            text="Jeżeli się cofasz, to tylko po to, żeby wziąć rozbieg.",
            font=("Arial", 12, "italic"),
            bg="white",
            fg="black"
        )
        footer_label.pack(side="top", pady=3, anchor="center")

        self.switch_view("lessons")  # Load the initial view

    def switch_view(self, view_name):
        """
        Switch the main container's content based on the selected view.
        :param view_name: Name of the view to load.
        """
        if self.current_frame:
            self.current_frame.destroy()  # Clear the current frame

        self.current_frame = tk.Frame(self.main_container, bg="white")
        self.current_frame.pack(fill="both", expand=True)

        if view_name == "lessons":
            self.display_table(self.current_frame, "lekcjeview")
        elif view_name == "students":
            self.display_table(self.current_frame, "uczen")
        else:
            tk.Label(self.current_frame, text=f"View: {view_name} (W budowie)", bg="white").pack(pady=20)

        # Add buttons at the bottom of the current frame
        self.add_action_buttons()

    def display_table(self, parent, view_name):
        """
        Display data from a database view in a table.
        :param parent: Parent frame to display the table.
        :param view_name: Name of the database view to fetch data from.
        """
        try:
            headers, data = self.db.fetch_all_from_view(view_name)
            if not data:
                tk.Label(parent, text="Brak danych do wyświetlenia.", font=("Arial", 10), bg="white").pack()
                return

            # Create the Treeview table
            tree = ttk.Treeview(parent, columns=headers, show="headings", selectmode="browse")
            tree.pack(fill="both", expand=True, pady=10)

            # Set column headers
            for col in headers:
                tree.heading(col, text=col)
                tree.column(col, anchor="center")

            # Insert rows
            for row in data:
                tree.insert("", "end", values=row)

            # Bind row click event
            tree.bind("<<TreeviewSelect>>", lambda e: self.on_row_click(tree))
        except Exception as e:
            tk.Label(parent, text=f"Błąd: {e}", font=("Arial", 10), bg="white", fg="red").pack(pady=10)

    def add_action_buttons(self):
        """
        Add buttons at the bottom of the current frame for actions.
        """
        buttons_frame = tk.Frame(self.current_frame, bg="white")
        buttons_frame.pack(side="bottom", fill="x", pady=10)

        btn1 = tk.Button(buttons_frame, text="Akcja 1", font=("Arial", 10), bg="white", command=self.action1)
        btn2 = tk.Button(buttons_frame, text="Akcja 2", font=("Arial", 10), bg="white", command=self.action2)
        btn3 = tk.Button(buttons_frame, text="Akcja 3", font=("Arial", 10), bg="white", command=self.action3)

        btn1.pack(side="left", padx=5)
        btn2.pack(side="left", padx=5)
        btn3.pack(side="left", padx=5)

    def on_row_click(self, tree):
        """
        Handle a row click in the table.
        :param tree: The Treeview widget.
        """
        selected_item = tree.selection()
        if selected_item:
            row_data = tree.item(selected_item, "values")
            print(f"Clicked row: {row_data}")  # Replace with edit functionality

    def action1(self):
        print("Akcja 1 wykonana")

    def action2(self):
        print("Akcja 2 wykonana")

    def action3(self):
        print("Akcja 3 wykonana")
