import tkinter as tk
from PIL import Image, ImageTk

# Tworzenie głównego okna
root = tk.Tk()
root.title("Dziennik szkolny")
root.geometry("750x700")  # Zmniejszamy szerokość okna
root.config(bg="gray")  # Ustawiamy tło całego okna na szare

# Górny pasek menu
menu_bar = tk.Frame(root, relief="groove", bd=2, bg="white")  # Tło menu na białe
menu_bar.pack(side="top", fill="x")

# Lewa część (Kto zalogowany)
kto_zalogowany = tk.Label(menu_bar, text="KTO ZALOGOWANI TZN (imię i nazwisko)", font=("Arial", 10), bg="white")  # Tło na białe
kto_zalogowany.pack(side="left", padx=10)

# Prawa część (Wyloguj jako przycisk)
wyloguj = tk.Button(menu_bar, text="WYLOGUJ", font=("Arial", 10), fg="black", bg="white")  # Kolor tekstu czarny, tło białe
wyloguj.pack(side="right", padx=10)

# Panel przycisków pod menu
toolbar = tk.Frame(root, relief="raised", bd=2, bg="white")  # Tło paska przycisków na białe
toolbar.pack(side="top", fill="x", pady=5, padx=10)

# Ikony emoji jako przyciski
icons = ["\u2709", "\U0001f393", "\U0001f514", "\U0001f4c5", "\u26a0", "\U0001f465"]
for icon in icons:
    button = tk.Button(toolbar, text=icon, font=("Arial", 14), width=6, height=3, fg="black", bg="white")  # Kolor tekstu czarny, tło białe, bez ramki
    button.pack(side="left", padx=10, pady=5)

# Dodanie logo szkoły tuż obok przycisków w toolbarze
try:
    image = Image.open("szkola_image.png")
    image = image.resize((130, 65), Image.LANCZOS)  # Zmniejszamy rozmiar logo
    logo = ImageTk.PhotoImage(image)
    logo_label = tk.Label(toolbar, image=logo, bg="white")  # Tło logo na białe
    logo_label.pack(side="left", padx=10)  # Zamiast grid, używamy pack, aby nie mieszać menedżerów
    logo_label.image = logo  # Zatrzymanie referencji
except Exception as e:
    print("Nie można załadować obrazu:", e)

# Kontener główny (bez scrolla)
frame = tk.Frame(root, bg="white")  # Tło obszaru na białe
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Dodanie cieńszego białego paska na dole z napisem
footer_frame = tk.Frame(root, bg="white", height=20)  # Cieńszy pasek na dole (wysokość 20)
footer_frame.pack(side="bottom", fill="x")

footer_label = tk.Label(footer_frame, text="Jeżeli się cofasz, to tylko po to, żeby wziąć rozbieg.",
                        font=("Arial", 12, "italic"), bg="white", fg="black")
footer_label.pack(side="top", pady=3, anchor="center")  # Umieszczamy napis w środku paska

root.mainloop()
