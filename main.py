# importy

import mysql.connector as mc
import cv2
from pyzbar.pyzbar import decode
import time


# łączenie z bazą
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': "Lojalnościowy_db"
}

conn = None

try:
    conn = mc.connect(**db_config)
    print("Połączono z bazą")

    cursor = conn.cursor()
    # Odpalanie kamery
    cap = cv2.VideoCapture(0)
    ostatnio_zeskanowane = {}

    if not cap.isOpened():
        print("Nie można otworzyć kamery!")
    else:
        print("Kamera uruchomiona, naciśnij Q aby wyjść")
        # czytanie kamery
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Błąd odczytu kamery")
                break

            zeskanowano = False
            # dekodowanie kodu qr ze zdjecia
            kody = decode(frame)

            for kod in kody:
                user_id = int(kod.data.decode("utf-8"))
                teraz = time.time()
                # ostatni skan zeby sie nie powtarzaly
                ostatni_skan = ostatnio_zeskanowane.get(user_id)

                if ostatni_skan is None or teraz - ostatni_skan > 30:
                    # update w bazie danych punktow uzytkownika
                    cursor.execute(
                        "UPDATE uzytkownicy SET liczba_punktów = liczba_punktów + 10 WHERE id = %s",
                        (user_id,)
                    )
                    conn.commit()

                    ostatnio_zeskanowane[user_id] = teraz
                    # Potwierdzenie o dodaniu do bazy
                    print(f"Dodano 10 punktów dla użytkownika {user_id}")
                    print("Dziękujemy za zakupy w naszym sklepie i za używanie naszej aplikacji <3")

                    zeskanowano = True
                    break

                else:
                    # zabezpieczenie jezeli kod juz zeskanowany
                    pozostalo = int(30 - (teraz - ostatni_skan))
                    print(f"Kod już zeskanowany, poczekaj {pozostalo}s...")

            if zeskanowano:
                #stop jezeli kod zeskanowany
                break
            # nazwa okna
            cv2.imshow("Skaner QR", frame)
            # offanie pod q ale nie dziala
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
# ewentualne błędy z baza danych
except mc.Error as err:
    print("Błąd z bazą:", err)

finally:
    if conn and conn.is_connected():
        cursor.close()
        conn.close()