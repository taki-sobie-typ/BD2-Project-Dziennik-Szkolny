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

    def delete_lesson(self, row_data):
        """
        Usuwa lekcję na podstawie ID lekcji.
        :param lesson_id: ID lekcji do usunięcia.
        """
        class_name, class_level, subject_name, date, hour_id, teacher_name, teacher_last_name = row_data
        lesson_id_result = self.db.execute_query(
            """
            SELECT l.lekcje_id 
            FROM lekcje l
            JOIN klasa k ON l.klasa_id = k.klasa_id
            JOIN przedmiot p ON l.przedmiot_id = p.przedmiot_id
            JOIN godziny g ON l.godzinygodzina_id = g.godzina_id
            JOIN nauczyciel n ON k.nauczyciel_wychowawca_id = n.nauczyciel_id
            JOIN dane_osobowe dn ON n.dane_osobowe_id = dn.id_dane_osobowe
            WHERE k.nazwa_klasy = %s
              AND k.poziom_klasy = %s
              AND p.nazwa_przedmiotu = %s
              AND l.data = %s
              AND g.godzina = %s
              AND dn.imie = %s
              AND dn.nazwisko = %s
            """,
            (class_name, class_level, subject_name, date, hour_id, teacher_name, teacher_last_name)
        )

        try:
            # Extracting lesson_id from the result (if there are any results)
            if lesson_id_result:
                lesson_id = lesson_id_result[0][0]  # Get the first value from the first tuple
            else:
                print(f"Lekcja o podanych danych nie istnieje.")
                return

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

    def edit_lesson(self, row_data):
        """
        Edytuje istniejącą lekcję na podstawie danych row_data.
        :param row_data: Dane lekcji w formacie
                         (class_name, lesson_id, subject_name, date, hour_id, teacher_name, teacher_last_name)
        """
        class_name, class_level, subject_name, date, hour_id, teacher_name, teacher_last_name = row_data

        # Tworzenie okna edycji lekcji
        edit_lesson_window = tk.Toplevel()
        edit_lesson_window.title("Edytuj lekcję")
        edit_lesson_window.geometry("400x400")

        # Pobieranie danych z bazy do comboboxów
        classes = self.db.execute_query("SELECT klasa_id, nazwa_klasy FROM klasa")
        subjects = self.db.execute_query("SELECT przedmiot_id, nazwa_przedmiotu FROM przedmiot")
        teachers = self.db.execute_query(
            "SELECT dn.imie, dn.nazwisko, n.nauczyciel_id FROM nauczyciel n JOIN dane_osobowe dn ON n.dane_osobowe_id = dn.id_dane_osobowe"
        )
        hours = self.db.execute_query("SELECT godzina_id, godzina FROM godziny")
        lesson_id_result = self.db.execute_query(
            """
            SELECT l.lekcje_id 
            FROM lekcje l
            JOIN klasa k ON l.klasa_id = k.klasa_id
            JOIN przedmiot p ON l.przedmiot_id = p.przedmiot_id
            JOIN godziny g ON l.godzinygodzina_id = g.godzina_id
            JOIN nauczyciel n ON k.nauczyciel_wychowawca_id = n.nauczyciel_id
            JOIN dane_osobowe dn ON n.dane_osobowe_id = dn.id_dane_osobowe
            WHERE k.nazwa_klasy = %s
              AND k.poziom_klasy = %s
              AND p.nazwa_przedmiotu = %s
              AND l.data = %s
              AND g.godzina = %s
              AND dn.imie = %s
              AND dn.nazwisko = %s
            """,
            (class_name, class_level, subject_name, date, hour_id, teacher_name, teacher_last_name)
        )

        if lesson_id_result:
            lesson_id = lesson_id_result[0][0]

        # Tworzenie formularza z predefiniowanymi wartościami
        class_label = tk.Label(edit_lesson_window, text="Klasa:")
        class_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.class_combobox = ttk.Combobox(
            edit_lesson_window, values=[f"{c[1]}" for c in classes]
        )
        self.class_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.class_combobox.set(class_name)

        subject_label = tk.Label(edit_lesson_window, text="Przedmiot:")
        subject_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.subject_combobox = ttk.Combobox(
            edit_lesson_window, values=[f"{s[1]}" for s in subjects]
        )
        self.subject_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.subject_combobox.set(subject_name)

        teacher_label = tk.Label(edit_lesson_window, text="Nauczyciel:")
        teacher_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.teacher_combobox = ttk.Combobox(
            edit_lesson_window, values=[f"{t[0]} {t[1]}" for t in teachers]
        )
        self.teacher_combobox.grid(row=2, column=1, padx=10, pady=5)
        self.teacher_combobox.set(f"{teacher_name} {teacher_last_name}")

        date_label = tk.Label(edit_lesson_window, text="Data lekcji:")
        date_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = tk.Entry(edit_lesson_window)
        self.date_entry.grid(row=3, column=1, padx=10, pady=5)
        self.date_entry.insert(0, date)

        hour_label = tk.Label(edit_lesson_window, text="Godzina lekcji:")
        hour_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.hour_combobox = ttk.Combobox(
            edit_lesson_window, values=[f"{h[1]}" for h in hours]
        )
        self.hour_combobox.grid(row=4, column=1, padx=10, pady=5)
        #self.hour_combobox.set(next((h[1] for h in hours if h[0] == hour_id), ""))
        self.hour_combobox.set(hour_id)

        # Przycisk do zatwierdzenia edycji lekcji
        submit_button = tk.Button(
            edit_lesson_window, text="Zapisz zmiany", command=lambda: self.submit_edited_lesson(lesson_id)
        )
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def submit_edited_lesson(self, lesson_id):
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

        # Znajdowanie ID na podstawie wybranego tekstu
        class_id = next(
            (c[0] for c in self.db.execute_query("SELECT klasa_id, nazwa_klasy FROM klasa") if c[1] == class_data),
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

        # Aktualizacja danych w bazie
        self.db.execute_update(
            "UPDATE lekcje SET data = %s, klasa_id = %s, przedmiot_id = %s, godzinygodzina_id = %s WHERE lekcje_id = %s",
            (date_data, class_id, subject_id, hour_id, lesson_id)
        )
        print("Lekcja została zaktualizowana.")
