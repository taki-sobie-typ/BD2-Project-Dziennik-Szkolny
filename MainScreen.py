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
        self.current_view = None  # Track the current view for action buttons
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
            "\U0001f465": "students",
            "\U0001F4DC": "grades"  # Ikona dla ocen
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
        self.add_action_buttons()

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

        self.current_view = view_name  # Update the current view

        if view_name == "lessons":
            self.display_table(self.current_frame, "lekcjeview")
        elif view_name == "students":
            self.display_table(self.current_frame, "uczniowie")
        elif view_name == "notifications":
            self.display_announcements(self.current_frame, "ogłoszenieview")
        elif view_name == "grades":
            self.display_table(self.current_frame, "ocena_widok")
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

    def display_announcements(self, parent, view_name):
        """
        Display announcements from a database view in a formatted layout.
        :param parent: Parent frame to display the announcements.
        :param view_name: Name of the database view to fetch data from.
        """
        try:
            # Fetch all data from the database view
            headers, data = self.db.fetch_all_from_view(view_name)
            if not data:
                tk.Label(parent, text="Brak ogłoszeń do wyświetlenia.", font=("Arial", 10), bg="white").pack()
                return

            # Pagination settings
            announcements_per_page = 3
            total_pages = (len(data) + announcements_per_page - 1) // announcements_per_page  # Round up division
            current_page = [0]  # Use a list to allow modification inside nested functions

            def show_announcement_popup(title, description, date_added, author_first_name, author_last_name):
                """Display a popup window with detailed announcement."""
                popup = tk.Toplevel(parent)
                popup.title("Szczegóły ogłoszenia")
                popup.geometry("500x400")
                popup.configure(bg="#f9f9f9")  # Subtle background color

                # Title
                title_label = tk.Label(
                    popup, text=title, font=("Arial", 14, "bold"), bg="#f9f9f9", anchor="center"
                )
                title_label.pack(fill="x", pady=(20, 10))

                # Description (limit to 255 characters)
                description = description[:255]
                description_label = tk.Label(
                    popup,
                    text=description,
                    font=("Arial", 11),
                    bg="#f9f9f9",
                    anchor="center",
                    wraplength=450,
                    justify="center",
                )
                description_label.pack(fill="x", padx=20, pady=(20, 30))

                # Date and Author
                footer_label = tk.Label(
                    popup,
                    text=f"Autor: {author_first_name} {author_last_name} | Data: {date_added}",
                    font=("Arial", 10),
                    bg="#f9f9f9",
                    fg="gray",
                    anchor="center",
                )
                footer_label.pack(fill="x", pady=(0, 20))

                # Close Button
                close_button = tk.Button(
                    popup, text="Zamknij", command=popup.destroy, bg="#d9d9d9", font=("Arial", 10)
                )
                close_button.pack(side="bottom", pady=20)

            def show_page(page):
                """Display the announcements for the specified page."""
                # Clear parent frame
                for widget in parent.winfo_children():
                    widget.destroy()

                # Calculate the range of announcements to display
                start_index = page * announcements_per_page
                end_index = start_index + announcements_per_page
                page_data = data[start_index:end_index]

                # Display announcements
                for row in page_data:
                    title, description, date_added, author_first_name, author_last_name = row

                    # Create a frame for each announcement
                    announcement_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=10)
                    announcement_frame.pack(fill="x", pady=5)

                    # Title
                    title_label = tk.Label(announcement_frame, text=title, font=("Arial", 12, "bold"), bg="white",
                                           anchor="w")
                    title_label.pack(fill="x")

                    # Short description
                    short_description = description[:100] + "..." if len(description) > 100 else description
                    description_label = tk.Label(
                        announcement_frame, text=short_description, font=("Arial", 10), bg="white", anchor="w",
                        wraplength=500
                    )
                    description_label.pack(fill="x", pady=5)

                    # Date and Author
                    footer_label = tk.Label(
                        announcement_frame,
                        text=f"Autor: {author_first_name} {author_last_name} | Data: {date_added}",
                        font=("Arial", 8), bg="white", anchor="w", fg="gray"
                    )
                    footer_label.pack(fill="x")

                    # Expand button
                    expand_button = tk.Button(
                        announcement_frame,
                        text="Rozwiń",
                        command=lambda t=title, d=description, da=date_added, af=author_first_name, al=author_last_name:
                        show_announcement_popup(t, d, da, af, al),
                        bg="lightblue", font=("Arial", 10)
                    )
                    expand_button.pack(side="right", padx=5, pady=5)

                # Navigation buttons
                nav_frame = tk.Frame(parent, bg="white", pady=10)
                nav_frame.pack(fill="x")

                # Previous Page Button
                if page > 0:
                    prev_button = tk.Button(
                        nav_frame, text="Poprzednia strona", command=lambda: show_page(page - 1), bg="lightgray"
                    )
                    prev_button.pack(side="left", padx=5)

                # Page Indicator
                page_label = tk.Label(nav_frame, text=f"Strona {page + 1} z {total_pages}", font=("Arial", 10),
                                      bg="white")
                page_label.pack(side="left", padx=5)

                # Next Page Button
                if page < total_pages - 1:
                    next_button = tk.Button(
                        nav_frame, text="Następna strona", command=lambda: show_page(page + 1), bg="lightgray"
                    )
                    next_button.pack(side="right", padx=5)

            # Show the first page initially
            show_page(current_page[0])

        except Exception as e:
            tk.Label(parent, text=f"Błąd: {e}", font=("Arial", 10), bg="white", fg="red").pack(pady=10)

    def add_action_buttons(self):
        # Find the existing buttons frame (assuming it was already created)
        buttons_frame = self.main_container.winfo_children()[0] if self.main_container.winfo_children() else None

        # If the buttons frame exists, clear it
        if buttons_frame:
            for widget in buttons_frame.winfo_children():
                widget.destroy()
        else:
            # If no buttons_frame exists, create one
            buttons_frame = tk.Frame(self.main_container, bg="lightgray")
            buttons_frame.pack(side="bottom", fill="x", pady=10)

        # Add buttons based on the current view
        if self.current_view == "grades":
            btn1 = tk.Button(buttons_frame, text="Dodaj ocenę", font=("Arial", 10), bg="white",
                             command=self.dodaj_ocene)
            btn2 = tk.Button(buttons_frame, text="Usuń ocenę", font=("Arial", 10), bg="white", command=self.usun_ocene)
            btn3 = tk.Button(buttons_frame, text="Edytuj ocenę", font=("Arial", 10), bg="white",
                             command=self.edytuj_ocene)
        elif self.current_view == "lessons":
            btn1 = tk.Button(buttons_frame, text="Dodaj lekcję", font=("Arial", 10), bg="white",
                             command=self.dodaj_lekcje)
            btn2 = tk.Button(buttons_frame, text="Usuń lekcję", font=("Arial", 10), bg="white",
                             command=self.usun_lekcje)
            btn3 = tk.Button(buttons_frame, text="Edytuj lekcję", font=("Arial", 10), bg="white",
                             command=self.edytuj_lekcje)
        elif self.current_view == "students":
            btn1 = tk.Button(buttons_frame, text="Dodaj ucznia", font=("Arial", 10), bg="white",
                             command=self.dodaj_ucznia)
            btn2 = tk.Button(buttons_frame, text="Usuń ucznia", font=("Arial", 10), bg="white",
                             command=self.usun_ucznia)
            btn3 = tk.Button(buttons_frame, text="Edytuj ucznia", font=("Arial", 10), bg="white",
                             command=self.edytuj_ucznia)
        else:
            # Default fallback button if no actions are available
            btn1 = btn2 = btn3 = tk.Button(buttons_frame, text="Brak akcji", font=("Arial", 10), bg="white")

        # Pack the buttons horizontally with some padding
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

    # Action methods for "grades"
    def dodaj_ocene(self):
        print("Dodaj ocenę")

    def usun_ocene(self):
        print("Usuń ocenę")

    def edytuj_ocene(self):
        print("Edytuj ocenę")

    # Action methods for "lessons"
    def dodaj_lekcje(self):
        print("Dodaj lekcję")

    def usun_lekcje(self):
        print("Usuń lekcję")

    def edytuj_lekcje(self):
        print("Edytuj lekcję")

    # Action methods for "students"
    def dodaj_ucznia(self):
        print("Dodaj ucznia")

    def usun_ucznia(self):
        print("Usuń ucznia")

    def edytuj_ucznia(self):
        print("Edytuj ucznia")
