import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



class Lekcja:
    def __init__(self, db_connection, user_data):
        self.db = db_connection
        self.user_data = user_data

    def dodaj_lekcje(self):
        # Tworzymy okno popup do dodania lekcji
        add_lesson_window = tk.Toplevel()
        add_lesson_window.title("Dodaj lekcję")
        add_lesson_window.geometry("400x400")

        # Pobieranie danych z bazy do comboboxów
        classes = self.db.execute_query("SELECT klasa_id, nazwa_klasy FROM klasa")
        subjects = self.db.execute_query("SELECT przedmiot_id, nazwa_przedmiotu FROM przedmiot")
        teachers = self.db.execute_query(
            "SELECT dn.imie, dn.nazwisko, n.nauczyciel_id FROM nauczyciel n JOIN dane_osobowe dn ON n.dane_osobowe_id = dn.id_dane_osobowe"
        )
        hours = self.db.execute_query("SELECT godzina_id, godzina FROM godziny")

        # Tworzenie formularza
        class_label = tk.Label(add_lesson_window, text="Klasa:")
        class_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.class_combobox = ttk.Combobox(
            add_lesson_window, values=[f"{c[1]}" for c in classes]
        )
        self.class_combobox.grid(row=0, column=1, padx=10, pady=5)

        subject_label = tk.Label(add_lesson_window, text="Przedmiot:")
        subject_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.subject_combobox = ttk.Combobox(
            add_lesson_window, values=[f"{s[1]}" for s in subjects]
        )
        self.subject_combobox.grid(row=1, column=1, padx=10, pady=5)

        teacher_label = tk.Label(add_lesson_window, text="Nauczyciel:")
        teacher_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.teacher_combobox = ttk.Combobox(
            add_lesson_window, values=[f"{t[0]} {t[1]}" for t in teachers]
        )
        self.teacher_combobox.grid(row=2, column=1, padx=10, pady=5)

        date_label = tk.Label(add_lesson_window, text="Data lekcji:")
        date_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = tk.Entry(add_lesson_window)
        self.date_entry.grid(row=3, column=1, padx=10, pady=5)

        hour_label = tk.Label(add_lesson_window, text="Godzina lekcji:")
        hour_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.hour_combobox = ttk.Combobox(
            add_lesson_window, values=[f"{h[1]}" for h in hours]
        )
        self.hour_combobox.grid(row=4, column=1, padx=10, pady=5)

        # Przycisk do zatwierdzenia dodania lekcji
        submit_button = tk.Button(
            add_lesson_window, text="Dodaj lekcję", command=self.submit_lesson
        )
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def submit_lesson(self):
        # Pobranie danych z formularza
        class_data = self.class_combobox.get()
        subject_data = self.subject_combobox.get()
        teacher_data = self.teacher_combobox.get()
        date_data = self.date_entry.get()
        hour_data = self.hour_combobox.get()

        # Walidacja danych
        if not class_data or not subject_data or not teacher_data or not date_data or not hour_data:
            print("Wszystkie pola muszą być wypełnione!")
            return

        # Pobranie nowego ID lekcji
        lekcje_id = self.db.execute_query("SELECT MAX(lekcje_id) FROM lekcje")[0][0] + 1

        # Znajdowanie ID na podstawie wybranego tekstu
        class_id = next(
            (c[0] for c in self.db.execute_query("SELECT klasa_id, nazwa_klasy FROM klasa") if c[1] in class_data),
            None)
        subject_id = next(
            (s[0] for s in self.db.execute_query("SELECT przedmiot_id, nazwa_przedmiotu FROM przedmiot") if
             s[1] == subject_data), None)
        teacher_id = next((t[2] for t in self.db.execute_query(
            "SELECT dn.imie, dn.nazwisko, n.nauczyciel_id FROM nauczyciel n JOIN dane_osobowe dn ON n.dane_osobowe_id = dn.id_dane_osobowe"
        ) if f"{t[0]} {t[1]}" == teacher_data), None)
        hour_id = self.db.execute_query(
            "SELECT godzina_id FROM godziny WHERE godzina = %s", (hour_data,)
        )[0][0]

        # Wstawianie danych do bazy
        self.db.execute_update(
            "INSERT INTO lekcje (lekcje_id, data, klasa_id, przedmiot_id, godzinygodzina_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (lekcje_id, date_data, class_id, subject_id, hour_id)
        )
        print("Lekcja została dodana.")

    def delete_lesson(self, lesson_id):
        """
        Usuwa lekcję na podstawie ID lekcji.
        :param lesson_id: ID lekcji do usunięcia.
        """
        try:
            # Sprawdzanie, czy lekcja istnieje
            existing_lesson = self.db.execute_query(
                "SELECT * FROM lekcje WHERE lekcje_id = %s", (lesson_id,)
            )
            if not existing_lesson:
                print(f"Lekcja o ID {lesson_id} nie istnieje.")
                return

            # Usuwanie lekcji
            self.db.execute_update(
                "DELETE FROM lekcje WHERE lekcje_id = %s", (lesson_id,)
            )
            print(f"Lekcja o ID {lesson_id} została pomyślnie usunięta.")
        except Exception as e:
            print(f"Wystąpił błąd podczas usuwania lekcji: {e}")
        print("Lekcja została usunięta!")
