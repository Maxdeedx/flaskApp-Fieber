from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import matplotlib
import datetime  # Für Zeitstempel
matplotlib.use("Agg")  # Headless-Backend für Matplotlib
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "geheimes_schluesselwort"

# Datei für die Speicherung der Temperaturen
DATA_FILE = "temperatures.txt"

def save_temperatures(data):
    """Speichert die Temperaturen und Zeitstempel in einer Datei."""
    print(f"[save_temperatures] Speichere in Datei: {data}")
    with open(DATA_FILE, "w") as file:
        for temp, timestamp in data:
            file.write(f"{temp},{timestamp}\n")

def load_temperatures():
    """Lädt die Temperaturen und Zeitstempel aus einer Datei."""
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            for line in file:
                if "," in line:  # Überprüfen, ob die Zeile ein Komma enthält
                    parts = line.strip().split(",")
                    try:
                        temp = float(parts[0])
                        timestamp = parts[1]
                        data.append((temp, timestamp))
                    except (ValueError, IndexError):
                        print(f"[load_temperatures] Ungültige Zeile übersprungen: {line.strip()}")
                else:
                    print(f"[load_temperatures] Ungültige Zeile ohne Komma: {line.strip()}")
    print(f"[load_temperatures] Geladene Daten aus Datei: {data}")
    return data


# Temporärer Speicher für die Temperaturen
temperatures = []

@app.route("/", methods=["GET", "POST"])
def home():
    global temperatures
    temperatures = load_temperatures()  # Datei immer neu laden
    print(f"[home] Nach Laden der Datei: {temperatures}")

    if request.method == "POST":
        temp = request.form.get("temperature")
        print(f"[home] Eingabe erhalten: {temp}")
        if temp:
            try:
                temp = float(temp)
                if 35 <= temp <= 43:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Zeitstempel erstellen
                    temperatures.append((temp, timestamp))
                    save_temperatures(temperatures)
                    create_chart([t[0] for t in temperatures])  # Nur Temperaturen für das Diagramm
                    print(f"[home] Nach Hinzufügen: {temperatures}")
                else:
                    flash(f"Ungültiger Wert: {temp}°C. Bitte nur Werte zwischen 35 und 43 eingeben.")
            except ValueError:
                flash("Ungültige Eingabe. Bitte eine Zahl eingeben.")

    return render_template("index.html", temperatures=temperatures)

from flask import Flask, render_template, request, send_file, flash, redirect, url_for
# Der Rest deines Imports bleibt gleich

@app.route("/clear", methods=["POST"])
def clear_data():
    """Löscht alle gespeicherten Temperaturen."""
    global temperatures
    print(f"[clear_data] Vor dem Löschen: {temperatures}")
    temperatures = []  # Liste zurücksetzen
    save_temperatures(temperatures)  # Datei leeren
    print(f"[clear_data] Nach dem Löschen: {temperatures}")
    flash("Alle gespeicherten Daten wurden gelöscht.")
    return redirect(url_for("home"))  # Leitet zurück auf die Startseite


def create_chart(data):
    """Erstellt ein Fieberkurven-Diagramm."""
    plt.figure(figsize=(8, 4))
    plt.plot(data, marker="o", color="red", linestyle="-")
    plt.title("Fieberkurve")
    plt.xlabel("Messung")
    plt.ylabel("Temperatur (°C)")

    # Dynamische y-Achse mit Puffer
    if data:
        plt.ylim(min(data) - 1, max(data) + 1)
    else:
        plt.ylim(35, 43)

    plt.grid(True)

    # Speicher das Diagramm
    chart_path = os.path.join("static", "chart.png")
    os.makedirs("static", exist_ok=True)
    plt.savefig(chart_path)
    plt.close()

@app.route("/chart")
def get_chart():
    """Sendet das Diagramm an den Browser."""
    return send_file(os.path.join("static", "chart.png"), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
