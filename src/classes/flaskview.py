from flask import Flask, jsonify, render_template, Request, request, redirect, Response
from threading import Thread
import logging as lg

from dataclasses import asdict
from src.classes.viewdatenmodell import ViewDatenmodell


class FlaskView:
    def __init__(self, logging: bool = False):
        self.app = Flask(__name__, template_folder='../../templates')

        # Logging deaktivieren:
        lg.disable(lg.CRITICAL)
        # Logging-Level anpassen (z.B. auf WARNING):
        lg.basicConfig(level=lg.WARNING)

        self.app.logger.disabled = not logging
        self.daten = ViewDatenmodell()
        self.web_kommando = None

        # Route für die HTML-Datei
        @self.app.route('/')
        @self.app.route('/index')
        def index():
            return render_template('index.html')

        @self.app.route('/get_data')
        def get_data():
            return jsonify(asdict(self.daten))

        # Routen mit den Befehlen
        @self.app.route('/pause')
        def pause() -> Response:
            self.browser_key = 'PAUSE'
            return redirect(request.referrer)

        @self.app.route('/musik_mute')
        def musik_mute() -> Response:
            self.browser_key = 'MUSIK_MUTE'
            return redirect(request.referrer)

        @self.app.route('/pwm_plusplus')
        def pwm_plusplus() -> Response:
            self.browser_key = 'PWM++'
            return redirect(request.referrer)

        @self.app.route('/pwm_plus')
        def pwm_plus() -> Response:
            self.browser_key = 'PWM+'
            return redirect(request.referrer)

        @self.app.route('/pwm_minus')
        def pwm_minus() -> Response:
            self.browser_key = 'PWM-'
            return redirect(request.referrer)

        @self.app.route('/pwm_minusminus')
        def pwm_minusminus() -> Response:
            self.browser_key = 'PWM--'
            return redirect(request.referrer)

        @self.app.route('/pause_nach_inhalt')
        def pause_nach_inhalt() -> Response:
            self.browser_key = 'PAUSE_NACH_INHALT'
            return redirect(request.referrer)

        @self.app.route('/change_trainigsprogramm_unendlich')
        def change_trainigsprogramm_unendlich() -> Response:
            self.browser_key = 'CHANGE_TRANINGSPROGRAMM_UNENDLICH'
            return redirect(request.referrer)

    def update(self, daten_modell):
        """Aktualisiert die anzuzeigenden Daten."""
        self.daten = daten_modell

    def draw_daten(self):
        pass

    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False, host='0.0.0.0')

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
