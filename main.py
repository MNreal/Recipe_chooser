
#importieren von web-Interface-modul
from flask import Flask, request, render_template_string, jsonify

#zum laden der json datei
import json

#ermöglicht zufällige Rezeptauswahl
import random

#Flask Anwendung initialisieren
app = Flask(__name__)

# Funktion zum Laden der Rezepte aus der JSON-Datei
def rezepte_laden(filename):

    #suche und ließ die json datei
    with open(filename, 'r') as f:
        #return das gelesene file
        return json.load(f)

# Rezepte laden
rezepte = rezepte_laden('rezepte.json')

# HTML-Vorlage
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ernährungscoach</title>
</head>
<body>
    <h1>Ernährungscoach</h1>
    <form id="filterForm">
        <label for="max_calories">Maximale Kalorien (in kcal):</label><br>
        <input type="number" id="max_calories" name="max_calories"><br><br>
        
        <label for="meals">Mahlzeiten:</label><br>
        <input type="checkbox" id="breakfast" name="meals" value="Frühstück">
        <label for="breakfast">Frühstück</label><br>
        <input type="checkbox" id="lunch" name="meals" value="Mittagessen">
        <label for="lunch">Mittagessen</label><br>
        <input type="checkbox" id="dinner" name="meals" value="Abendessen">
        <label for="dinner">Abendessen</label><br><br>
        
        <label for="vegetarian_vegan">Ernährungsweise:</label><br>
        <input type="radio" id="any" name="vegetarian_vegan" value="any" checked>
        <label for="any">Beliebig</label><br>
        <input type="radio" id="vegetarian" name="vegetarian_vegan" value="vegetarisch">
        <label for="vegetarian">Vegetarisch</label><br>
        <input type="radio" id="vegan" name="vegetarian_vegan" value="vegan">
        <label for="vegan">Vegan</label><br><br>
        
        <input type="button" value="Rezepte suchen" onclick="submitForm()">
    </form>
    
    <h2>Rezeptvorschläge:</h2>
    <div id="recipes"></div>
    
    <script>
        function submitForm() {
            var form = document.getElementById('filterForm');
            var formData = new FormData(form);
            var jsonData = {};
            formData.forEach((value, key) => {
                if (key === "meals") {
                    if (!jsonData[key]) {
                        jsonData[key] = [];
                    }
                    jsonData[key].push(value);
                } else {
                    jsonData[key] = value;
                }
            });

            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => response.json())
            .then(data => {
                var recipesDiv = document.getElementById('recipes');
                recipesDiv.innerHTML = "";
                if (data.length === 0) {
                    recipesDiv.innerHTML = "<p>Keine Rezepte gefunden.</p>";
                } else {
                    data.forEach(recipe => {
                        recipesDiv.innerHTML += `<h3>${recipe.name}</h3>
                                                 <p>Kalorien: ${recipe.calories} kcal</p>
                                                 <p>Mahlzeit: ${recipe.meal_type}</p>
                                                 <p>Zutaten: ${recipe.ingredients}</p>
                                                 <p>Zubereitung: ${recipe.preparation}</p>
                                                 <hr>`;
                    });
                }
            });
        }
    </script>
</body>
</html>
'''

#definiere den Endpunkt der Indexsseite der Website
@app.route('/')

def index():
    #redndern der Html vorlage
    return render_template_string(HTML_TEMPLATE)

#definition des Empfänger Endpunktes
@app.route('/submit', methods=['POST'])

def submit():
    #entnehmen der Daten aus dem json file
    data = request.json
    #maximale kalorien
    max_calories = int(data['max_calories'])
    #ernährungsfilter verwenden
    vegetarian_vegan = data.get('vegetarian_vegan', 'any')
    #ausgewähltes Essen extrahieren
    meals = data.get('meals', [])

    #filter anwenden
    filtered_recipes = [r for r in rezepte if r['meal_type'] in meals]
    
    # falls eine spezifische Ernährungsweise ausgewählt wurde
    if vegetarian_vegan != 'any':
        filtered_recipes = [r for r in filtered_recipes if r['vegetarian_vegan'] == vegetarian_vegan]
    
    # initialisieren einer leeren Liste für ausgewählte Rezepte und Variable für die Gesamtkalorien
    selected_recipes = []
    total_calories = 0

    # über jede ausgewählte Mahlzeit iterieren
    for meal in meals:
        # filtern der Rezepte nur für diese Mahlzeit
        meal_recipes = [r for r in filtered_recipes if r['meal_type'] == meal]
        # wenn Rezepte für diese Mahlzeit 
        if meal_recipes:
            # zufällige Auswahl eines Rezepts für diese Mahlzeit
            selected_recipe = random.choice(meal_recipes)
            # prüfen, ob das Hinzufügen dieses Rezepts maximale Kalorienbeschränkung nicht überschreitet
            if total_calories + selected_recipe['calories'] <= max_calories:
                # hinzufügen des ausgewählten Rezepts zur Liste der ausgewählten Rezepte
                selected_recipes.append(selected_recipe)
                # aktualisieren der Gesamtkalorien um die Kalorien dieses Rezepts
                total_calories += selected_recipe['calories']
    #rezept als json antwort ausgeben
    return jsonify(selected_recipes)

#starte das programm
if __name__ == '__main__':
    app.run(debug=True)
