import qrcode
from qrcode.image.pil import PilImage
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread

beende_anzeige = []


def generate_qr_code(data: str) -> PilImage:
    """Generiert einen QR-Code und gibt ihn als PIL-Image zurück.

    Args:
        data (str): Die Daten, die im QR-Code codiert werden sollen.

    Returns:
        PIL.Image: Das erzeugte QR-Code-Bild.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def show_qr_code_in_tkinter(img: Image.Image, schliesse_window: list) -> None:
    """Zeigt den QR-Code in einem Tkinter-Fenster an.
    Kann mit <q>, <ESC> oder <Enter> geschlossen werden.
    Vom aufrufenden Programm aus kann das Fenster mit close_window gesteuert werden.

    Args:
        img (PIL.Image): Das QR-Code-Bild.
        schliesse_window: Die Liste fuer die Abbruchbedingung
    """

    def close_window(event):
        schliesse_window.append(True)

    window = tk.Tk()
    window.title("QR-Code")

    # Konvertiere das PIL-Image in ein PhotoImage für Tkinter
    photo = ImageTk.PhotoImage(img)  # Vereinfachte Syntax

    label = tk.Label(window, image=photo)
    label.pack()
    window.bind("<q>", close_window)
    window.bind("<Escape>", close_window)
    window.bind("<Return>", close_window)

    close_flag = False

    while not schliesse_window:
        window.update()

    schliesse_window.clear()
    print("Close")
    window.destroy()


def zeige_qr_code_in_tkinter(img: PilImage, schliesse_window: list) -> Thread:
    """Starte die TKinter-Funktion als Thread"""
    tk_thread = Thread(target=show_qr_code_in_tkinter, args=(img, schliesse_window))
    tk_thread.start()
    return tk_thread


if __name__ == '__main__':
    # Beispielaufruf
    url = "HalloWelt.com"
    qr_img = generate_qr_code(url)
    print(f"{ isinstance(qr_img, PilImage)}")
    zeige_qr_code_in_tkinter(qr_img, beende_anzeige)
    import time
    time.sleep(3)
    beende_anzeige.append(True)
    time.sleep(0.3)
    print(f"{beende_anzeige = }")
