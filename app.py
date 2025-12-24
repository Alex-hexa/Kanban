from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "kanban_data.json"
CATEGORIES_FILE = "categories.json"

# Colonnes officielles
DEFAULT_COLUMNS = ["Pense bête", "À faire", "En cours", "Terminé"]


def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_categories(categories):
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)


def find_category(cat_id, categories):
    for c in categories:
        if c["id"] == cat_id:
            return c
    return None


def update_ticket_categories_by_date(data):
    today = datetime.today().date()
    for col in data:
        for ticket in data[col]:
            date_str = ticket.get("date", "").strip()
            if not date_str:
                continue
            try:
                ticket_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                days_left = (ticket_date - today).days
            except Exception:
                continue

            if days_left <= 3:
                ticket["category"] = 1
            elif 4 <= days_left <= 8:
                ticket["category"] = 2
            elif 9 <= days_left <= 15:
                ticket["category"] = 3
            elif days_left >= 16:
                ticket["category"] = 4


def empty_data():
    """Crée une structure vide avec les colonnes officielles."""
    return {col: [] for col in DEFAULT_COLUMNS}


def load_data():
    """Charge les données depuis le JSON, ou structure vide si problème."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            print("Erreur de chargement JSON:", e)
            return empty_data()

        data = empty_data()
        for col in DEFAULT_COLUMNS:
            if col in raw and isinstance(raw[col], list):
                data[col] = raw[col]
        return data

    return empty_data()


def save_data(data):
    """Sauvegarde les données dans le JSON (seulement colonnes officielles)."""
    cleaned = empty_data()
    for col in DEFAULT_COLUMNS:
        if col in data and isinstance(data[col], list):
            cleaned[col] = data[col]

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Erreur de sauvegarde JSON:", e)


@app.route("/")
def index():
    data = load_data()
    update_ticket_categories_by_date(data)
    save_data(data)
    categories = load_categories()
    return render_template(
        "index.html",
        columns=DEFAULT_COLUMNS,
        tickets=data,
        categories=categories
    )


@app.route("/add", methods=["POST"])
def add_ticket():
    data = load_data()
    column = request.form["column"]
    title = request.form["title"].strip()
    comment = request.form.get("comment", "").strip()
    category = request.form.get("category", "").strip()
    date = request.form.get("date", "").strip()

    if category:
        try:
            category = int(category)
        except ValueError:
            category = None
    else:
        category = None

    if column not in data:
        return redirect(url_for("index"))

    if title:
        ticket = {
            "title": title,
            "comment": comment
        }
        if category:
            ticket["category"] = category
        if date:
            ticket["date"] = date
        data[column].append(ticket)

        update_ticket_categories_by_date(data)
        save_data(data)

    return redirect(url_for("index"))


@app.route("/delete", methods=["POST"])
def delete_ticket():
    data = load_data()
    column = request.form.get("column")
    index = request.form.get("index")

    try:
        index = int(index)
    except (ValueError, TypeError):
        return redirect(url_for("index"))

    if column in data and 0 <= index < len(data[column]):
        del data[column][index]
        save_data(data)

    return redirect(url_for("index"))


@app.route("/move", methods=["POST"])
def move_ticket():
    data = load_data()
    from_column = request.form["from_column"]
    to_column = request.form["to_column"]
    try:
        from_index = int(request.form["from_index"])
    except (ValueError, TypeError):
        return ("", 400)

    if from_column not in data or to_column not in data:
        return ("", 400)
    if not (0 <= from_index < len(data[from_column])):
        return ("", 400)

    ticket = data[from_column].pop(from_index)
    data[to_column].append(ticket)
    save_data(data)

    return ("", 204)


@app.route("/edit", methods=["POST"])
def edit_ticket():
    data = load_data()
    column = request.form.get("column")
    index = request.form.get("index")
    new_title = request.form.get("new_title", "").strip()
    new_comment = request.form.get("new_comment", "").strip()
    category = request.form.get("edit_category", "").strip()
    date = request.form.get("date", "").strip()

    if category:
        try:
            category = int(category)
        except ValueError:
            category = None
    else:
        category = None

    try:
        index = int(index)
    except (ValueError, TypeError):
        return redirect(url_for("index"))

    if column in data and 0 <= index < len(data[column]) and new_title:
        data[column][index]["title"] = new_title
        data[column][index]["comment"] = new_comment
        if category:
            data[column][index]["category"] = category
        else:
            data[column][index].pop("category", None)
        if date:
            data[column][index]["date"] = date
        else:
            data[column][index].pop("date", None)

        update_ticket_categories_by_date(data)
        save_data(data)

    return redirect(url_for("index"))


@app.route("/categories", methods=["GET"])
def api_get_categories():
    return jsonify(load_categories())


@app.route("/category", methods=["POST"])
def create_category():
    categories = load_categories()
    data = request.json
    new_id = max([c["id"] for c in categories], default=0) + 1
    new_cat = {"id": new_id, "name": data["name"], "color": data["color"]}
    categories.append(new_cat)
    save_categories(categories)
    return jsonify(new_cat), 201


@app.route("/category/<int:cat_id>", methods=["PATCH"])
def update_category(cat_id):
    categories = load_categories()
    data = request.json
    for cat in categories:
        if cat["id"] == cat_id:
            cat["name"] = data.get("name", cat["name"])
            cat["color"] = data.get("color", cat["color"])
            save_categories(categories)
            return jsonify(cat)
    return '', 404


@app.route("/category/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    categories = load_categories()
    categories = [c for c in categories if c["id"] != cat_id]
    save_categories(categories)
    return '', 204


if __name__ == "__main__":
    app.run(debug=True)