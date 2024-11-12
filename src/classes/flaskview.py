from flask import Flask, jsonify, render_template
from threading import Thread

from src.classes.viewdatenmodell import ViewDatenModell


class FlaskView:
    def __init__(self, logging: bool = False):
        self.app = Flask(__name__)
        self.app.logger.disabled = not logging
        self.daten = ViewDatenModell()
        self.browser_key = 'Inikey'

        # Route für die HTML-Datei
        @self.app.route('/')
        def index():
            return render_template('index.html')

        # Route, um die aktuellen Daten abzurufen
        @self.app.route('/ergometer')
        def get_data():
            return jsonify(self.daten._asdict())

        @self.app.route('/input', methods=['POST'])
        def process_input():
            input_data = request.json  # Erwartet eine JSON-Nachricht
            print("Request angekommen")
            if 'key' in input_data:
                key = input_data['key']
                self.browser_key = key  # Speichere den letzten Schlüssel
                print(jsonify({"status": "success", "key": key}))
                return jsonify({"status": "success", "key": key})
            return jsonify({"status": "error", "message": "No key provided"}), 400

    def update(self, daten_modell):
        """Aktualisiert die anzuzeigenden Daten."""
        self.daten = daten_modell

    def draw_daten(self):
        pass

    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False)

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
