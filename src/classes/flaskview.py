from typing import Callable
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

        self.web_kommando_mappings = {
            'pause': 'PAUSE',
            'musik_mute': 'MUSIK_MUTE',
            'pwm_plusplus': 'PWM++',
            'pwm_plus': 'PWM+',
            'pwm_minusminus': 'PWM--',
            'pwm_minus': 'PWM-',
            'pause_nach_inhalt': 'PAUSE_NACH_INHALT',
            'change_trainigsprogramm_unendlich': 'CHANGE_TRANINGSPROGRAMM_UNENDLICH'
        }
        self.register_kommando_routes()
        self.define_manual_routes()

    def define_manual_routes(self):
        # Route für die HTML-Datei
        @self.app.route('/')
        @self.app.route('/index')
        def index():
            return render_template('index.html')

        @self.app.route('/get_data')
        def get_data():
            return jsonify(asdict(self.daten))

    def register_kommando_routes(self) -> None:
        """Registriert dynamisch einfache Routen."""
        for route, command in self.web_kommando_mappings.items():
            self.app.add_url_rule(f'/{route}', route, self.create_kommando_route_handler(command))

    def create_kommando_route_handler(self, command: str) -> Callable[[], Response]:
        """Erstellt einen Routen-Handler für einen bestimmten Befehl."""
        def handler() -> Response:
            self.browser_key = command
            return redirect(request.referrer)

        return handler

    def update(self, daten_modell: ViewDatenmodell) -> None:
        """Aktualisiert die anzuzeigenden Daten."""
        self.daten = daten_modell

    def draw_daten(self) -> None:
        pass

    def run(self) -> None:
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False, host='0.0.0.0')

    def start_server(self) -> None:
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
