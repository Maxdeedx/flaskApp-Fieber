from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import matplotlib
import datetime  # Für Zeitstempel
matplotlib.use("Agg")  # Headless-Backend für Matplotlib
import matplotlib.pyplot as plt
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "geheimes_schluesselwort"

# Datenbankkonfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Datenbank-Modell
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.String, nullable=False)

def create_chart():
    """Erstellt ein Fieberkurven-Diagramm aus den aktuellen Daten der Datenbank."""
    data = [entry.temperature for entry in Temperature.query.all()]
    timestamps = [entry.timestamp for entry in Temperature.query.all()]

    plt.figure(figsize=(8, 4))
    plt.plot(data, marker="o", color="red", linestyle="-")
    plt.title("Fieberkurve")
    plt.xlabel("Messung")
    plt.ylabel("Temperatur (°C)")

    # Dynamische y-Achse mit Puffer
    if data:
        plt.ylim(min(data) - 1, max(data) + 1)
        plt.xticks(range(len(timestamps)), timestamps, rotation=45, fontsize=8)  # Zeitstempel als x-Achse
    else:
        plt.ylim(35, 43)

    plt.grid(True)

    # Speicher das Diagramm
    chart_path = os.path.join("static", "chart.png")
    os.makedirs("static", exist_ok=True)
    plt.tight_layout()  # Verhindert Überlappung der Achsentexte
    plt.savefig(chart_path)
    plt.close()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        temp = request.form.get("temperature")
        if temp:
            try:
                temp = float(temp)
                if 35 <= temp <= 43:
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    new_measurement = Temperature(temperature=temp, timestamp=timestamp)
                    db.session.add(new_measurement)
                    db.session.commit()
                    create_chart()  # Aktualisiere das Diagramm
                    flash("Temperatur erfolgreich hinzugefügt!")
                else:
                    flash(f"Ungültiger Wert: {temp}°C. Bitte nur Werte zwischen 35 und 43 eingeben.")
            except ValueError:
                flash("Ungültige Eingabe. Bitte eine Zahl eingeben.")

    # Daten aus der Datenbank abrufen
    measurements = Temperature.query.all()
    return render_template("index.html", measurements=measurements)

@app.route("/clear", methods=["POST"])
def clear_data():
    db.session.query(Temperature).delete()
    db.session.commit()
    create_chart()  # Aktualisiere das Diagramm
    flash("Alle Daten gelöscht!")
    return redirect("/")

@app.route("/chart")
def get_chart():
    """Sendet das Diagramm an den Browser."""
    return send_file(os.path.join("static", "chart.png"), mimetype="image/png")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Erstelle die Datenbank, falls sie noch nicht existiert
        create_chart()  # Initiales Diagramm erstellen
    app.run(debug=True, port=8080)
