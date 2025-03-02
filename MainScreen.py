import tkinter as tk
from tkinter import ttk, Toplevel
from PIL import Image, ImageTk

from Lekcja import Lekcja
from Ocena import *
from tkcalendar import DateEntry
from datetime import datetime, timedelta


class SchoolDiaryApp:
    def __init__(self, root, db_connection, user_data):
        self.root = root
        self.db = db_connection
        self.user_data = user_data  # Store the user data
        self.ocena = Ocena(db_connection, user_data)
        self.lekcja = Lekcja(db_connection, user_data)
        self.selected_grade_id = None
        self.selected_lesson_id = None
        self.row_data = None

        self.icons = {
            "\u2709": "messages",
            "\U0001f514": "notifications",
            "\U0001f4c5": "calendar",
            "\U0001F4DC": "grades",  # Icon for grades
            "\U0001f393": "lessons",
            "\U0001f465": "students"
        }

        # Define available icons for each user level
        self.icon_sets = {
            3: ["\u2709", "\U0001f514", "\U0001f4c5", "\U0001F4DC", "\U0001f393", "\U0001f465"],  # Administrator
            2: ["\u2709", "\U0001f514", "\U0001f4c5", "\U0001F4DC", "\U0001f393"],  # Teacher
            1: ["\u2709", "\U0001f514", "\U0001f4c5", "\U0001F4DC"],  # Parent
            0: ["\u2709", "\U0001f514", "\U0001f4c5", "\U0001F4DC"],  # Student
        }


    def start(self):
        # Initialize the main screen frame
        self.main_screen_frame = tk.Frame(self.root)
        self.main_screen_frame.pack(fill="both", expand=True)

        self.root.title("Dziennik szkolny")
        self.root.geometry("1200x750")
        self.root.config(bg="lightgray")
        self.root.resizable(False, False)

        self.current_frame = None  # To track the currently displayed content
        self.current_view = None  # Track the current view for action buttons
        self.create_ui()

    def create_ui(self):
        # Toolbar (inside main_screen_frame)
        self.toolbar = tk.Frame(self.main_screen_frame, relief="raised", bd=2, bg="white")
        self.toolbar.pack(side="top", fill="x", pady=5, padx=10)

        allowed_icons = self.icon_sets.get(self.user_data.get("user_level"), [])

        for icon_unicode in allowed_icons:
            view = self.icons.get(icon_unicode)  # Get the view corresponding to the icon

            button = tk.Button(
                self.toolbar, text=icon_unicode, font=("Arial", 14), width=6, height=3,
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

        # Scrollable main container (inside main_screen_frame)
        self.main_container = tk.Frame(self.main_screen_frame, bg="white")
        self.main_container.pack(padx=10, pady=10, fill="both", expand=True)

        # Footer (inside main_screen_frame)
        footer_frame = tk.Frame(self.main_screen_frame, bg="white", height=20)
        footer_frame.pack(side="bottom", fill="x")

        footer_label = tk.Label(
            footer_frame,
            text="Jeżeli się cofasz, to tylko po to, żeby wziąć rozbieg.",
            font=("Arial", 12, "italic"),
            bg="white",
            fg="black"
        )
        footer_label.pack(side="top", pady=3, anchor="center")

        self.add_action_buttons()  # You may need to define this method or replace it as per your need

        # Switch to the initial view (lessons)
        self.switch_view("lessons")



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
            self.panel_administratora(self.current_frame)
        elif view_name == "notifications":
            self.display_announcements(self.current_frame, "ogłoszenieview")
        elif view_name == "grades":
            self.display_table(self.current_frame, "ocena_widok")
        elif view_name == "messages":
            self.display_messages(self.current_frame)
        elif view_name == "calendar":
            self.display_schedule(self.current_frame)

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

    def display_messages(self, parent):
        """
        Display messages from the database view in a formatted layout.
        :param parent: Parent frame to display the messages.
        """
        try:
            # Variables for message type selection
            message_type = ["received", "sent"]  # This will hold the types: received or sent
            current_message_type = [
                "received"]  # Default to 'received' as a list to allow modification inside functions

            selected_messages = set()  # Track selected messages for deletion

            # Create frames for message type buttons and message content
            message_type_frame = tk.Frame(parent, bg="white")
            message_type_frame.pack(fill="x", pady=10)

            messages_frame = tk.Frame(parent, bg="white")
            messages_frame.pack(fill="both", expand=True)

            def fetch_and_display_messages(message_type):
                """Fetch and display messages based on selected type."""
                # Fetch all data from the database view based on message type
                headers, data = self.db.fetch_messages(self.user_data['user_id'], message_type)
                if not data:
                    for widget in messages_frame.winfo_children():
                        widget.destroy()
                    tk.Label(messages_frame, text="Brak wiadomości do wyświetlenia.", font=("Arial", 10),
                             bg="white").pack()
                    return

                # Pagination settings
                messages_per_page = 3
                total_pages = (len(data) + messages_per_page - 1) // messages_per_page  # Round up division
                current_page = [0]  # Use a list to allow modification inside nested functions

                # Function to show message page
                show_message_page(current_page[0], data, total_pages, current_page, message_type)

            def show_message_page(page, data, total_pages, current_page, message_type):
                """Display the messages for the specified page."""
                # Clear only the messages frame
                for widget in messages_frame.winfo_children():
                    widget.destroy()

                # Calculate the range of messages to display
                start_index = page * 3
                end_index = start_index + 3
                page_data = data[start_index:end_index]

                # Display messages
                for index, row in enumerate(page_data):
                    date_sent, title, description, author_first_name, author_last_name = row

                    # Create a frame for each message
                    message_frame = tk.Frame(messages_frame, bg="white", bd=1, relief="solid", padx=10, pady=10)
                    message_frame.pack(fill="x", pady=5)

                    # Title with checkbox
                    title_frame = tk.Frame(message_frame, bg="white")
                    title_frame.pack(fill="x")

                    # Title Label
                    title_label = tk.Label(title_frame, text=title, font=("Arial", 12, "bold"), bg="white", anchor="w")
                    title_label.pack(fill="x", side="left")

                    # Short description
                    short_description = description[:100] + "..." if len(description) > 100 else description
                    description_label = tk.Label(
                        message_frame, text=short_description, font=("Arial", 10), bg="white", anchor="w",
                        wraplength=500
                    )
                    description_label.pack(fill="x", pady=5)

                    footer_label_text = (
                        f"Autor: {author_first_name} {author_last_name} | Data: {date_sent}"
                        if message_type == "received"
                        else f"Odbiorca: {author_first_name} {author_last_name} | Data: {date_sent}"
                    )

                    # Date and Author
                    footer_label = tk.Label(
                        message_frame,
                        text=footer_label_text,
                        font=("Arial", 8), bg="white", anchor="w", fg="gray"
                    )
                    footer_label.pack(fill="x")

                    # Expand button
                    expand_button = tk.Button(
                        message_frame,
                        text="Rozwiń",
                        command=lambda t=title, d=description, da=date_sent, af=author_first_name, al=author_last_name:
                        show_message_popup(t, d, da, af, al, message_type),
                        bg="lightblue", font=("Arial", 10)
                    )
                    expand_button.pack(side="right", padx=5, pady=5)

                # Navigation buttons
                nav_frame = tk.Frame(messages_frame, bg="white", pady=10)
                nav_frame.pack(fill="x")

                # Previous Page Button
                if page > 0:
                    prev_button = tk.Button(
                        nav_frame, text="Poprzednia strona",
                        command=lambda: show_message_page(page - 1, data, total_pages, current_page, message_type), bg="lightgray"
                    )
                    prev_button.pack(side="left", padx=5)

                # Page Indicator
                page_label = tk.Label(nav_frame, text=f"Strona {page + 1} z {total_pages}", font=("Arial", 10),
                                      bg="white")
                page_label.pack(side="left", padx=5)

                # Next Page Button
                if page < total_pages - 1:
                    next_button = tk.Button(
                        nav_frame, text="Następna strona",
                        command=lambda: show_message_page(page + 1, data, total_pages, current_page, message_type), bg="lightgray"
                    )
                    next_button.pack(side="right", padx=5)

                # Add Message Button
                add_message_button = tk.Button(
                    nav_frame, text="Dodaj wiadomość", command=add_new_message, bg="lightblue"
                )
                add_message_button.pack(side="right", padx=5)

            def add_new_message():
                """Display a popup window for adding a new message."""
                popup = tk.Toplevel(parent)
                popup.title("Dodaj wiadomość")
                popup.geometry("700x700")  # Powiększone okno
                popup.configure(bg="#f9f9f9")

                # Title input
                title_label = tk.Label(popup, text="Tytuł:", font=("Arial", 14), bg="#f9f9f9")
                title_label.pack(pady=(20, 5), anchor="w", padx=20)
                title_entry = tk.Entry(popup, font=("Arial", 14), width=60)  # Szeroki entry
                title_entry.pack(pady=10, padx=20)

                # Description input
                description_label = tk.Label(popup, text="Treść:", font=("Arial", 14), bg="#f9f9f9")
                description_label.pack(pady=10, anchor="w", padx=20)
                description_entry = tk.Text(popup, font=("Arial", 14), width=60, height=10)  # Większe pole tekstowe
                description_entry.pack(pady=10, padx=20)

                # Recipient selection
                recipient_label = tk.Label(popup, text="Wybierz odbiorców:", font=("Arial", 14), bg="#f9f9f9")
                recipient_label.pack(pady=(20, 5), anchor="w", padx=20)

                # Symulacja listy odbiorców z bazy danych
                recipients = self.db.fetch_recipients_from_db()

                # Przykład poprawionego kodu:
                recipient_names = []  # Lista do przechowywania nazw odbiorców

                # Iterujemy przez odbiorców i formatujemy nazwę w zależności od typu użytkownika
                for recipient in recipients:
                    # Ustalamy typ odbiorcy
                    if recipient['typ'] == 'nauczyciel':
                        formatted_name = f"{recipient['imie']} {recipient['nazwisko']} - nauczyciel"
                    elif recipient['typ'] == 'administrator':
                        formatted_name = f"{recipient['imie']} {recipient['nazwisko']} - administrator"
                    elif recipient['typ'] == 'uczen':
                        # Zakładamy, że klasa jest dostępna w polu 'klasa'
                        klasa = recipient.get('klasa', 'brak klasy')
                        formatted_name = f"{recipient['imie']} {recipient['nazwisko']} - {klasa}"
                    else:  # Zakładamy, że jeśli typ to rodzic
                        formatted_name = f"{recipient['imie']} {recipient['nazwisko']}"

                    # Dodajemy nazwisko w odpowiednim formacie do listy
                    recipient_names.append(formatted_name)

                    # Listbox z wielokrotnym wyborem
                listbox = tk.Listbox(popup, selectmode=tk.MULTIPLE, font=("Arial", 14), height=6, width=50)
                listbox.pack(pady=10, padx=20)

                # Dodajemy odbiorców do listboxa
                for name in recipient_names:
                    listbox.insert(tk.END, name)

                # Funkcja do wyświetlania wybranych odbiorców
                def show_selected_recipients():
                    selected_indices = listbox.curselection()  # Pobieramy zaznaczone indeksy
                    selected_ids = [recipients[i]['id_uzytkownika'] for i in selected_indices]  # Mapujemy indeksy na ID
                    title = title_entry.get().strip()
                    description = description_entry.get("1.0", tk.END).strip()
                    # recipient = recipient_entry.get().strip()
                    if not title or not description or not recipient:
                        print("Wszystkie pola muszą być wypełnione.")
                        return

                    self.db.send_messages(title, description, selected_ids, self.user_data["user_id"])
                    popup.destroy()
                    fetch_and_display_messages(current_message_type[0])

                # Przycisk do zatwierdzenia wyboru
                button = tk.Button(popup, text="Zatwierdź", font=("Arial", 14), command=show_selected_recipients)
                button.pack(pady=10)

                # Uruchamiamy okno popup
                popup.mainloop()

            def show_message_popup(title, description, date_sent, author_first_name, author_last_name, message_type):
                """Display a popup window with detailed message."""
                popup = tk.Toplevel(parent)
                popup.title("Szczegóły wiadomości")
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

                footer_label_text = (
                    f"Autor: {author_first_name} {author_last_name} | Data: {date_sent}"
                    if message_type == "received"
                    else f"Odbiorca: {author_first_name} {author_last_name} | Data: {date_sent}"
                )

                # Date and Author
                footer_label = tk.Label(
                    popup,
                    text=footer_label_text,
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
            def toggle_message_selection(message_index, checkbox_var):
                """Toggle the selection of a message for deletion."""
                if checkbox_var.get():
                    selected_messages.add(message_index)
                else:
                    selected_messages.discard(message_index)

            def switch_message_type(new_type):
                """Switch between 'sent' and 'received' messages."""
                if new_type != current_message_type[0]:
                    current_message_type[0] = new_type
                    for widget in messages_frame.winfo_children():
                        widget.destroy()
                    fetch_and_display_messages(new_type)

            # Add buttons for selecting message type
            received_button = tk.Button(
                message_type_frame, text="Odebrane", command=lambda: switch_message_type("received"), bg="lightgreen"
            )
            received_button.pack(side="left", padx=5)

            sent_button = tk.Button(
                message_type_frame, text="Wysłane", command=lambda: switch_message_type("sent"), bg="lightblue"
            )
            sent_button.pack(side="left", padx=5)

            # Fetch and display the initial 'received' messages
            fetch_and_display_messages("received")

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
            selected_announcements = set()  # Track selected announcements for deletion

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

            def delete_selected_announcements():
                """Delete selected announcements from the database."""
                if not selected_announcements:
                    print("No announcements selected for deletion.")
                    return
                # Delete logic, assuming you have a delete method in your DB class
                self.db.delete_announcements(list(selected_announcements))
                selected_announcements.clear()
                self.display_announcements(parent, view_name) # Refresh the page after deletion

            def add_new_announcement():
                """Display a popup window for adding a new announcement."""
                popup = tk.Toplevel(parent)
                popup.title("Dodaj ogłoszenie")
                popup.geometry("600x450")  # Increased window size
                popup.configure(bg="#f9f9f9")

                # Title input
                title_label = tk.Label(popup, text="Tytuł:", font=("Arial", 16), bg="#f9f9f9")
                title_label.pack(pady=(20, 5), anchor="w", padx=20)  # Left-align and add padding
                title_entry = tk.Entry(popup, font=("Arial", 16), width=50)  # Increased width
                title_entry.pack(pady=10, padx=20)

                # Description input
                description_label = tk.Label(popup, text="Opis:", font=("Arial", 16), bg="#f9f9f9")
                description_label.pack(pady=10, anchor="w", padx=20)  # Left-align and add padding
                description_entry = tk.Text(popup, font=("Arial", 16), width=50, height=8)  # Larger text area
                description_entry.pack(pady=10, padx=20)

                def add_announcement_to_db():
                    """Add the new announcement to the database."""
                    title = title_entry.get()
                    description = description_entry.get("1.0", tk.END).strip()
                    if not title or not description:
                        print("Title and description cannot be empty.")
                        return
                    # Add logic, assuming you have an add method in your DB class
                    self.db.add_announcement(title, description, self.user_data)
                    popup.destroy()
                    self.display_announcements(parent, view_name)

                # Add Button
                add_button = tk.Button(popup, text="Dodaj", command=add_announcement_to_db, bg="lightgreen",
                                       font=("Arial", 16))
                add_button.pack(pady=20)

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
                for index, row in enumerate(page_data):
                    ogloszenie_id, title, description, date_added, author_first_name, author_last_name = row

                    # Create a frame for each announcement
                    announcement_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=10)
                    announcement_frame.pack(fill="x", pady=5)

                    # Title with checkbox
                    title_frame = tk.Frame(announcement_frame, bg="white")
                    title_frame.pack(fill="x")

                    # Checkbox for deletion
                    checkbox_var = tk.BooleanVar()
                    checkbox = tk.Checkbutton(
                        title_frame, variable=checkbox_var, bg="white", selectcolor="lightgray",
                        command=lambda idx=ogloszenie_id, var=checkbox_var: toggle_selection(idx, var)
                    )
                    checkbox.pack(side="left", padx=5)

                    # Title Label
                    title_label = tk.Label(title_frame, text=title, font=("Arial", 12, "bold"), bg="white", anchor="w")
                    title_label.pack(fill="x", side="left")

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

                # Add Announcement Button
                add_button = tk.Button(
                    nav_frame, text="Dodaj ogłoszenie", command=add_new_announcement, bg="lightblue"
                )
                add_button.pack(side="right", padx=5)

                # Delete Selected Button
                delete_button = tk.Button(
                    nav_frame, text="Usuń wybrane", command=delete_selected_announcements, bg="lightcoral"
                )
                delete_button.pack(side="right", padx=5)

            def toggle_selection(announcement_index, checkbox_var):
                """Toggle the selection of an announcement for deletion."""
                if checkbox_var.get():
                    selected_announcements.add(announcement_index)
                else:
                    selected_announcements.discard(announcement_index)

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

        if(self.user_data.get("user_level")>1):
            # Add buttons based on the current view
            if self.current_view == "grades":
                btn1 = tk.Button(buttons_frame, text="Dodaj ocenę", font=("Arial", 10), bg="white",
                                 command=self.dodaj_ocene)
                btn2 = tk.Button(buttons_frame, text="Usuń ocenę", font=("Arial", 10), bg="white", command=self.usun_ocene)
                btn3 = tk.Button(buttons_frame, text="Edytuj ocenę", font=("Arial", 10), bg="white",
                                 command=self.edytuj_ocene)
                # Pack the buttons horizontally with some padding
                btn1.pack(side="left", padx=5)
                btn2.pack(side="left", padx=5)
                btn3.pack(side="left", padx=5)
            elif self.current_view == "lessons":
                btn1 = tk.Button(buttons_frame, text="Dodaj lekcję", font=("Arial", 10), bg="white",
                                 command=self.dodaj_lekcje)
                btn2 = tk.Button(buttons_frame, text="Usuń lekcję", font=("Arial", 10), bg="white",
                                 command=self.usun_lekcje)
                btn3 = tk.Button(buttons_frame, text="Edytuj lekcję", font=("Arial", 10), bg="white",
                                 command=self.edytuj_lekcje)
                # Pack the buttons horizontally with some padding
                btn1.pack(side="left", padx=5)
                btn2.pack(side="left", padx=5)
                btn3.pack(side="left", padx=5)


    global grade_id

    def on_row_click(self, tree):
        """
        Handle a row click in the table.
        :param tree: The Treeview widget.
        """
        selected_item = tree.selection()
        if selected_item:
            row_data = tree.item(selected_item, "values")
            self.selected_grade_id = row_data[0]
            self.selected_lesson_id = row_data[1]
            self.row_data = row_data
            print(f"Clicked row: {row_data}")  # Replace with edit functionality

    # Action methods for "grades"
    def dodaj_ocene(self):
        print("Dodaj ocenę")
        self.ocena.dodaj_ocene()

    def usun_ocene(self):
        print("Usuń ocenę")
        if self.selected_grade_id is None:
            print("Nie wybrano oceny do usunięcia.")
            return

        self.ocena.delete_grade(self.selected_grade_id)
        self.selected_grade_id = None


    def edytuj_ocene(self):
        print("Edytuj ocenę")
        self.ocena.edytuj_ocene(self.row_data)
    # Action methods for "lessons"
    def dodaj_lekcje(self):
        print("Dodaj lekcję")
        self.lekcja.dodaj_lekcje()


    def usun_lekcje(self): #Do poprawy!!!!!!!!
        print("Usuń lekcję")
        if self.row_data is None:
            print("Nie wybrano lekcji do usunięcia.")
            return

        self.lekcja.delete_lesson(self.row_data)
        self.selected_grade_id = None

    def edytuj_lekcje(self):
        print("Edytuj lekcję")
        self.lekcja.edit_lesson(self.row_data)

    # Action methods for "students"
    def dodaj_ucznia(self):
        print("Dodaj ucznia")

    def usun_ucznia(self):
        print("Usuń ucznia")

    def edytuj_ucznia(self):
        print("Edytuj ucznia")

    def hide_main_screen(self):
        self.main_screen_frame.pack_forget()  # Destroy the login screen frame completely

    def show_main_screen(self):
        self.main_screen_frame.pack(fill="both", expand=True)  # Re-show the login screen

    def set_user_data(self, user_data):
        self.user_data = user_data

    def display_schedule(self, parent_frame):
        """
        Wyświetl widok kalendarza z planem zajęć na podstawie wybranej daty.
        :param parent_frame: Rodzic dla komponentów kalendarza.
        """
        class_list = self.db.get_classes_list()

        # Aktualna klasa i data wybrana przez użytkownika
        self.selected_class = tk.StringVar(value="1A")
        self.start_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        def update_schedule():
            # Pobranie zajęć dla wybranej klasy
            selected_class_name = self.selected_class.get()
            # Zmieniamy start_date na datetime obiekt
            start_date = datetime.strptime(self.start_date.get(), "%Y-%m-%d")

            # Pobieramy plan zajęć z bazy danych dla wybranej klasy i daty
            filtered_schedule = self.db.get_classes(selected_class_name, start_date)

            # Renderowanie zajęć
            render_schedule(filtered_schedule, start_date)

        # Combobox dla wyboru klasy
        tk.Label(parent_frame, text="Wybierz klasę:", font=("Arial", 12), bg="white").pack(pady=5, anchor="w")
        class_combobox = ttk.Combobox(parent_frame, textvariable=self.selected_class, values=list(class_list),
                                      state="readonly", font=("Arial", 12))
        class_combobox.pack(pady=5, anchor="w")
        class_combobox.bind("<<ComboboxSelected>>", lambda e: update_schedule())

        # DateEntry dla wyboru daty
        tk.Label(parent_frame, text="Wybierz datę początkową:", font=("Arial", 12), bg="white").pack(pady=5, anchor="w")
        date_entry = DateEntry(parent_frame, textvariable=self.start_date, date_pattern="yyyy-MM-dd",
                               font=("Arial", 12))
        date_entry.pack(pady=5, anchor="w")
        date_entry.bind("<<DateEntrySelected>>", lambda e: update_schedule())

        # Ramka na kalendarz
        calendar_frame = tk.Frame(parent_frame, bg="white")
        calendar_frame.pack(fill="both", expand=True, pady=10)

        day_names_map = {
            "Mon": "Pon",
            "Tue": "Wt",
            "Wed": "Śr",
            "Thu": "Czw",
            "Fri": "Pt",
            "Sat": "Sob",
            "Sun": "Ndz"
        }

        def render_schedule(schedule, start_date):
            # Wyczyść poprzedni harmonogram
            for widget in calendar_frame.winfo_children():
                widget.destroy()

            # Utworzenie nagłówków kolumn na 5 kolejnych dni z nazwami dni tygodnia
            days = [(start_date + timedelta(days=i)) for i in range(5)]  # 5 dni od start_date
            for col, day in enumerate(days):
                day_name = day.strftime("%a")  # Pobieramy angielski skrót dnia tygodnia
                day_name_polish = day_names_map.get(day_name, day_name)  # Tłumaczymy na polski
                header = tk.Label(calendar_frame, text=f"{day.strftime('%Y-%m-%d')}\n{day_name_polish}",
                                  font=("Arial", 12, "bold"), bg="lightblue", width=15, height=2)
                header.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

            # Grupowanie zajęć według daty
            day_schedules = {day.strftime("%Y-%m-%d"): [] for day in days}

            # Uzupełnianie planu zajęć według daty
            for lesson_date, lessons in schedule.items():
                if lesson_date in day_schedules:
                    for godzina_rozpoczecia, przedmiot in lessons:
                        day_schedules[lesson_date].append((godzina_rozpoczecia, przedmiot))

            # Wyświetlanie zajęć w kalendarzu
            for day, lessons in day_schedules.items():
                for lesson in lessons:
                    godzina_rozpoczecia, przedmiot = lesson
                    # Formatowanie godziny w odpowiedni sposób (jeśli jest w formacie HH:MM:SS, możemy usunąć sekundy)
                    godzina_str = godzina_rozpoczecia[:5]  # Usuwamy sekundy, jeżeli istnieją

                    lesson_text = f"{godzina_str}\n{przedmiot}"
                    lesson_label = tk.Label(calendar_frame, text=lesson_text, font=("Arial", 10), bg="white",
                                            relief="solid", wraplength=100)

                    # Określamy wiersz (począwszy od 1) dla każdego przedmiotu w tym dniu
                    lesson_label.grid(row=lessons.index(lesson) + 1,
                                      column=days.index(datetime.strptime(day, "%Y-%m-%d")),
                                      sticky="nsew", padx=5, pady=5)

            # Dodanie rozciągania kolumn
            for col in range(len(days)):
                calendar_frame.columnconfigure(col, weight=1)

        # Renderowanie początkowego harmonogramu
        update_schedule()

    def panel_administratora(self, current_frame):

        # Create a frame inside the panel for the buttons
        panel_frame = tk.Frame(self.current_frame, bg="white")
        panel_frame.pack(fill="both", expand=True)

        # Create a container (sub-frame) for the buttons to center them horizontally but position them higher
        button_frame = tk.Frame(panel_frame, bg="white")
        button_frame.pack(side="top", pady=50)  # This moves the buttons higher by adding a padding on top

        # Create button data with button text and associated command
        button_data = [
            ("Uczniowie", self.open_students_popup),
            ("Nauczyciele", self.open_teachers_popup),
            ("Rodzice", self.open_parents_popup),
            ("Klasy", self.open_classes_popup)
        ]

        # Place the buttons in a 2x2 grid inside the centered button_frame
        for index, (text, command) in enumerate(button_data):
            row = index // 2  # Integer division to get the row (0 or 1)
            col = index % 2  # Modulo operation to get the column (0 or 1)
            button = tk.Button(button_frame, text=text, font=("Arial", 16), width=20, height=3, command=command)
            button.grid(row=row, column=col, padx=10, pady=10)  # Place the button in the grid

    def open_students_popup(self):
        popup = Toplevel(self.root)
        popup.title("Dodaj Nowego Ucznia")
        popup.geometry("400x800")  # Adjusted size for input fields

        # Add a title label
        title_label = tk.Label(popup, text="Dodaj Nowego Ucznia", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Create labels and entry fields for student data
        labels_and_fields = [
            ("Imię:", "imie"),
            ("Nazwisko:", "nazwisko"),
            ("Data urodzenia (YYYY-MM-DD):", "data_urodzenia"),
            ("Numer kontaktowy:", "numer_kontaktowy"),
            ("Adres zamieszkania (ulica, miasto, kod pocztowy, kraj):", "adres"),
            ("Numer budynku:", "numer_budynku"),
            ("Numer mieszkania:", "numer_mieszkania"),
            ("Płeć (M/F):", "plec"),
            ("Nazwa użytkownika:", "nazwa_uzytkownika"),
            ("Hasło:", "haslo"),
            ("Email:", "email"),
        ]

        input_fields = {}  # Dictionary to store input field references

        for text, field_name in labels_and_fields:
            label = tk.Label(popup, text=text, font=("Arial", 12))
            label.pack(anchor="w", padx=10, pady=5)
            entry = tk.Entry(popup, font=("Arial", 12))
            entry.pack(fill="x", padx=10, pady=5)
            input_fields[field_name] = entry  # Save entry field in the dictionary

        # Submit button
        def submit_student_data():
            # Retrieve data from input fields
            try:
                imie = input_fields["imie"].get()
                nazwisko = input_fields["nazwisko"].get()
                data_urodzenia = input_fields["data_urodzenia"].get()
                numer_kontaktowy = input_fields["numer_kontaktowy"].get()
                adres = input_fields["adres"].get()
                numer_budynku = input_fields["numer_budynku"].get()
                numer_mieszkania = input_fields["numer_mieszkania"].get()
                plec = input_fields["plec"].get()
                nazwa_uzytkownika = input_fields["nazwa_uzytkownika"].get()
                haslo = input_fields["haslo"].get()
                email = input_fields["email"].get()

                # Split address fields
                ulica, miasto, kod_pocztowy, kraj = adres.split(", ")

                # Insert data in correct order
                id_adres = self.add_address(numer_budynku, numer_mieszkania, ulica, miasto, kod_pocztowy)
                if not id_adres:
                    raise ValueError("Błąd podczas dodawania adresu.")

                id_dane_osobowe = self.add_personal_data(
                    imie, nazwisko, data_urodzenia, numer_kontaktowy, id_adres, plec
                )
                if not id_dane_osobowe:
                    raise ValueError("Błąd podczas dodawania danych osobowych.")

                id_uzytkownik = self.add_user(nazwa_uzytkownika, haslo, email)
                if not id_uzytkownik:
                    raise ValueError("Błąd podczas dodawania użytkownika.")

                self.add_role(id_uzytkownik, "uczen", id_dane_osobowe)
                print(f"Uczeń '{imie} {nazwisko}' został pomyślnie dodany.")
                popup.destroy()

            except Exception as e:
                print(f"Błąd: {e}")

        submit_button = tk.Button(
            popup, text="Dodaj Ucznia", font=("Arial", 12, "bold"), bg="green", fg="white",
            command=submit_student_data
        )
        submit_button.pack(pady=20)

        # Close button
        close_button = tk.Button(popup, text="Zamknij", font=("Arial", 12), command=popup.destroy)
        close_button.pack(pady=10)

    def open_teachers_popup(self):
        popup = Toplevel(self.root)
        popup.title("Nauczyciele")
        popup.geometry("300x200")
        label = tk.Label(popup, text="Panel Nauczycieli", font=("Arial", 14))
        label.pack(pady=50)
        # Add more widgets or functionality to this popup as needed

    def open_parents_popup(self):
        popup = Toplevel(self.root)
        popup.title("Rodzice")
        popup.geometry("300x200")
        label = tk.Label(popup, text="Panel Rodziców", font=("Arial", 14))
        label.pack(pady=50)
        # Add more widgets or functionality to this popup as needed

    def open_classes_popup(self):
        popup = Toplevel(self.root)
        popup.title("Klasy")
        popup.geometry("300x200")
        label = tk.Label(popup, text="Panel Klas", font=("Arial", 14))
        label.pack(pady=50)