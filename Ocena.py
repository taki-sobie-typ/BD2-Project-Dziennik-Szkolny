class Ocena:
    def dodaj_ocene(self, przedmiot_id, wartosc_oceny, data_przyznania, waga, poprawiona_ocena,
                    nauczyciel_oceniający_id, uczen_id):
        """
        Dodaj nową ocenę do bazy danych.
        """
        try:
            query = """
                INSERT INTO ocena (przedmiot_id, wartosc_oceny, data_przyznania, waga, poprawiona_ocena, nauczyciel_oceniający_id, uczen_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
            przedmiot_id, wartosc_oceny, data_przyznania, waga, poprawiona_ocena, nauczyciel_oceniający_id, uczen_id)
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Dodano nową ocenę do bazy danych.")
        except Exception as e:
            print("Błąd przy dodawaniu oceny:", e)
            raise