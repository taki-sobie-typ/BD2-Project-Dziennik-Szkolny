import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime


class Ocena:
    def __init__(self, db_connection, user_data):
        self.db = db_connection
        self.user_data = user_data

    def delete_grade(self, grade_id):
        """
        Usuwa ocenę na podstawie ID oceny.
        :param grade_id: ID oceny do usunięcia.
        """
        try:
            # Sprawdzanie, czy ocena istnieje
            existing_grade = self.db.execute_query(
                "SELECT * FROM ocena WHERE ocena_id = %s", (grade_id,)
            )
            if not existing_grade:
                print(f"Ocena o ID {grade_id} nie istnieje.")
                return

            # Usuwanie oceny
            self.db.execute_update(
                "DELETE FROM ocena WHERE ocena_id = %s", (grade_id,)
            )
            print(f"Ocena o ID {grade_id} została pomyślnie usunięta.")
        except Exception as e:
            print(f"Wystąpił błąd podczas usuwania oceny: {e}")
        print("Ocena została usunięta!")

    def edytuj_ocene(self, row_data):
        print("Edytuj ocenę")

        # Tworzymy okno wyskakujące (popup)
        edit_grade_window = tk.Toplevel()
        edit_grade_window.title("Edytuj ocenę")
        edit_grade_window.geometry("400x400")

        # Rozpakowanie danych z zaznaczonego wiersza
        ocena_id, przedmiot_id, wartosc_oceny, data_przyznania, waga, poprawiona_ocena, nauczyciel_oceniajacy_id, uczen_id = row_data

        # Pobieranie danych (przedmioty, uczniowie) z bazy danych
        subjects = self.db.execute_query("SELECT przedmiot_id, nazwa_przedmiotu FROM przedmiot")
        students = self.db.execute_query(
            "SELECT dn.imie, dn.nazwisko, u.uczen_id FROM uczen u JOIN dane_osobowe dn ON u.dane_osobowe_id = dn.id_dane_osobowe")

        # Formularz
        subject_label = tk.Label(edit_grade_window, text="Przedmiot:")
        subject_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.subject_combobox = ttk.Combobox(
            edit_grade_window,
            values=[f"{s[1]}" for s in subjects]
        )
        self.subject_combobox.grid(row=0, column=1, padx=10, pady=5)
        # Ustawienie domyślnego przedmiotu
        current_subject = next((s[1] for s in subjects if s[0] == przedmiot_id), "")
        self.subject_combobox.set(current_subject)

        student_label = tk.Label(edit_grade_window, text="Uczeń:")
        student_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.student_combobox = ttk.Combobox(
            edit_grade_window,
            values=[f"{s[0]} {s[1]}" for s in students]
        )
        self.student_combobox.grid(row=1, column=1, padx=10, pady=5)
        # Ustawienie domyślnego ucznia
        current_student = next((f"{s[0]} {s[1]}" for s in students if s[2] == uczen_id), "")
        self.student_combobox.set(current_student)

        grade_label = tk.Label(edit_grade_window, text="Ocena:")
        grade_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.grade_combobox = ttk.Combobox(
            edit_grade_window,
            values=["1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0"]
        )
        self.grade_combobox.grid(row=2, column=1, padx=10, pady=5)
        self.grade_combobox.set(wartosc_oceny)  # Ustawienie bieżącej wartości oceny

        improved_grade_label = tk.Label(edit_grade_window, text="Poprawiona Ocena:")
        improved_grade_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.improved_grade_combobox = ttk.Combobox(
            edit_grade_window,
            values=["1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0"]
        )
        self.improved_grade_combobox.grid(row=3, column=1, padx=10, pady=5)
        self.improved_grade_combobox.set(
            poprawiona_ocena if poprawiona_ocena else "")  # Ustawienie poprawionej oceny (lub pustego pola)

        weight_label = tk.Label(edit_grade_window, text="Waga:")
        weight_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.weight_entry = tk.Entry(edit_grade_window)
        self.weight_entry.grid(row=4, column=1, padx=10, pady=5)
        self.weight_entry.insert(0, str(waga))  # Ustawienie bieżącej wagi

        # Informacja o nowej dacie
        date_label = tk.Label(edit_grade_window,
                              text=f"Data zostanie zmieniona na dzisiejszą: {datetime.now().strftime('%Y-%m-%d')}")
        date_label.grid(row=5, column=0, columnspan=2, pady=5)

        # Przycisk do zapisania edycji
        submit_button = tk.Button(edit_grade_window, text="Zatwierdź", command=lambda: self.submit_edit(ocena_id))
        submit_button.grid(row=6, column=0, columnspan=2, pady=10)

    def submit_edit(self, ocena_id):
        # Pobieranie danych z formularza
        subject_name = self.subject_combobox.get()
        student_name = self.student_combobox.get()
        grade_value = self.grade_combobox.get()
        improved_grade_value = self.improved_grade_combobox.get()
        weight = self.weight_entry.get()
        grade_date = datetime.now().strftime("%Y-%m-%d")  # Automatyczne ustawienie bieżącej daty

        # Walidacja danych
        if not subject_name or not grade_value or not weight or not student_name:
            print("Wszystkie pola muszą być wypełnione.")
            return

        # Pobranie ID przedmiotu
        subject_id = self.db.execute_query(
            "SELECT przedmiot_id FROM przedmiot WHERE nazwa_przedmiotu = %s", (subject_name,)
        )
        if not subject_id:
            print(f"Nie znaleziono przedmiotu: {subject_name}")
            return
        subject_id = subject_id[0][0]

        # Pobranie ID ucznia
        student_first_name, student_last_name = student_name.split()
        student_id = self.db.execute_query(
            "SELECT u.uczen_id FROM uczen u "
            "JOIN dane_osobowe dn ON u.dane_osobowe_id = dn.id_dane_osobowe "
            "WHERE dn.imie = %s AND dn.nazwisko = %s", (student_first_name, student_last_name)
        )
        if not student_id:
            print(f"Nie znaleziono ucznia: {student_first_name} {student_last_name}")
            return
        student_id = student_id[0][0]

        # Aktualizacja oceny w bazie danych
        self.db.execute_update(
            "UPDATE ocena SET przedmiot_id = %s, wartosc_oceny = %s, data_przyznania = %s, waga = %s, poprawiona_ocena = %s, uczen_id = %s "
            "WHERE ocena_id = %s",
            (
            subject_id, grade_value, grade_date, weight, improved_grade_value if improved_grade_value else None,
            student_id, ocena_id)
        )
        print("Ocena została pomyślnie zaktualizowana!")

    def dodaj_ocene(self):
        print("Dodaj ocenę")
        # Tworzymy okno wyskakujące (popup)
        add_grade_window = tk.Toplevel()
        add_grade_window.title("Dodaj ocenę")
        add_grade_window.geometry("400x300")

        # Pobieranie danych (przedmioty, uczniowie) z bazy danych
        subjects = self.db.execute_query("SELECT nazwa_przedmiotu FROM przedmiot")
        students = self.db.execute_query(
            "SELECT dn.imie, dn.nazwisko FROM uczen u JOIN dane_osobowe dn ON u.dane_osobowe_id = dn.id_dane_osobowe")

        # Formularz
        subject_label = tk.Label(add_grade_window, text="Przedmiot:")
        subject_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.subject_combobox = ttk.Combobox(add_grade_window, values=[s[0] for s in subjects])
        self.subject_combobox.grid(row=0, column=1, padx=10, pady=5)

        student_label = tk.Label(add_grade_window, text="Uczeń:")
        student_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.student_combobox = ttk.Combobox(add_grade_window, values=[f"{s[0]} {s[1]}" for s in students])
        self.student_combobox.grid(row=1, column=1, padx=10, pady=5)

        grade_label = tk.Label(add_grade_window, text="Ocena:")
        grade_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.grade_combobox = ttk.Combobox(add_grade_window,
                                           values=["1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5",
                                                   "6.0"])
        self.grade_combobox.grid(row=2, column=1, padx=10, pady=5)

        weight_label = tk.Label(add_grade_window, text="Waga:")
        weight_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.weight_entry = tk.Entry(add_grade_window)
        self.weight_entry.grid(row=3, column=1, padx=10, pady=5)

        # Informacja o dacie
        date_label = tk.Label(add_grade_window,
                              text=f"Data (ustawiona automatycznie): {datetime.now().strftime('%Y-%m-%d')}")
        date_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Przycisk do zapisania oceny
        submit_button = tk.Button(add_grade_window, text="Zatwierdź", command=self.submit_grade)
        submit_button.grid(row=5, column=0, columnspan=2, pady=10)

    def submit_grade(self):
        # Pobieranie danych z formularza
        subject = self.subject_combobox.get()
        grade_value = self.grade_combobox.get()
        weight = self.weight_entry.get()
        student_name = self.student_combobox.get()
        grade_date = datetime.now().strftime("%Y-%m-%d")  # Ustawienie bieżącej daty

        # Walidacja danych
        if not subject or not grade_value or not weight or not student_name:
            print("Wszystkie pola muszą być wypełnione.")
            return

        try:
            # Parsowanie daty
            grade_date_obj = datetime.strptime(grade_date, "%Y-%m-%d")
        except ValueError:
            print("Błąd formatu daty. Użyj formatu YYYY-MM-DD.")
            return

        # Rozdzielenie imienia i nazwiska ucznia
        student_first_name, student_last_name = student_name.split()

        # Pobranie ID przedmiotu
        subject_id = self.db.execute_query(
            "SELECT przedmiot_id FROM przedmiot WHERE nazwa_przedmiotu = %s", (subject,)
        )
        if not subject_id:
            print(f"Nie znaleziono przedmiotu: {subject}")
            return
        subject_id = subject_id[0][0]

        # Pobranie ID ucznia
        student_id = self.db.execute_query(
            "SELECT u.uczen_id FROM uczen u "
            "JOIN dane_osobowe dn ON u.dane_osobowe_id = dn.id_dane_osobowe "
            "WHERE dn.imie = %s AND dn.nazwisko = %s", (student_first_name, student_last_name)
        )
        if not student_id:
            print(f"Nie znaleziono ucznia: {student_first_name} {student_last_name}")
            return
        student_id = student_id[0][0]

        increment_id = self.db.execute_query("SELECT MAX(ocena_id) FROM ocena")

        # Jeżeli wynik jest None (brak rekordów), ustawiamy increment_id na 1
        increment_id = increment_id[0][0] if increment_id[0][0] is not None else 0

        # Zwiększanie increment_id o 1
        increment_id += 1

        teacher_id = self.user_data.get("user_id")

        # Dodanie oceny do bazy danych
        self.db.execute_update(
            "INSERT INTO ocena (ocena_id ,przedmiot_id, wartosc_oceny, data_przyznania, waga, poprawiona_ocena, nauczyciel_oceniajacy_id, uczen_id) "
            "VALUES (%s, %s, %s, %s, %s, NULL, %s, %s)",
            (increment_id, subject_id, grade_value, grade_date_obj, weight, teacher_id, student_id)
        )
        print("Ocena została pomyślnie dodana!")
