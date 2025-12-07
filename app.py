from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Meal, Favorite, planner_table
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
CORS(app)

with app.app_context():
    db.create_all()

# MEALS 
@app.route("/meals", methods=["GET"])
def get_meals():
    meals = Meal.query.all()
    return jsonify([meal.to_dict() for meal in meals])

@app.route("/meals", methods=["POST"])
def add_meal():
    data = request.get_json()
    new_meal = Meal(
        name=data.get("name"),
        image=data.get("image"),
        ingredients=data.get("ingredients"),
        instructions=data.get("instructions"),
    )
    db.session.add(new_meal)
    db.session.commit()
    return jsonify(new_meal.to_dict()), 201

@app.route("/meals/<int:meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Meal deleted"})

# FAVORITES 
@app.route("/favorites", methods=["GET"])
def get_favorites():
    favorites = Favorite.query.options(joinedload(Favorite.meal)).all()
    return jsonify([f.meal.to_dict() for f in favorites])

@app.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json()
    meal_id = data.get("meal_id")
    if not meal_id:
        return jsonify({"error": "meal_id is required"}), 400
    exists = Favorite.query.filter_by(meal_id=meal_id).first()
    if exists:
        return jsonify({"message": "Already favorite"}), 200
    fav = Favorite(meal_id=meal_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.meal.to_dict()), 201

@app.route("/favorites/<int:meal_id>", methods=["DELETE"])
def delete_favorite(meal_id):
    fav = Favorite.query.filter_by(meal_id=meal_id).first_or_404()
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite removed"})

# WEEKLY PLANNER 
@app.route("/planner", methods=["GET"])
def get_planner():
    results = db.session.execute(planner_table.select()).fetchall()
    planner = [{"day": r.day, "meal_id": r.meal_id} for r in results]
    return jsonify(planner)

@app.route("/planner/<day>", methods=["POST"])
def add_to_planner(day):
    meal_id = request.args.get("meal_id")
    if not meal_id:
        return jsonify({"error": "meal_id query param required"}), 400
    exists = db.session.execute(
        planner_table.select().where(
            (planner_table.c.day == day) & (planner_table.c.meal_id == meal_id)
        )
    ).first()
    if exists:
        return jsonify({"message": "Meal already in planner"}), 200
    db.session.execute(
        planner_table.insert().values(day=day, meal_id=meal_id)
    )
    db.session.commit()
    return jsonify({"message": "Meal added to planner"}), 201

@app.route("/planner/<day>/<int:meal_id>", methods=["DELETE"])
def remove_from_planner(day, meal_id):
    db.session.execute(
        planner_table.delete().where(
            (planner_table.c.day == day) & (planner_table.c.meal_id == meal_id)
        )
    )
    db.session.commit()
    return jsonify({"message": "Meal removed from planner"})

# GROCERIES 
@app.route("/groceries", methods=["GET"])
def get_groceries():
    results = db.session.execute(planner_table.select()).fetchall()
    groceries = {}
    for r in results:
        meal = Meal.query.get(r.meal_id)
        if meal and meal.ingredients:
            for ing in meal.ingredients.split(","):
                ing = ing.strip()
                groceries[ing] = groceries.get(ing, 0) + 1
    items = [{"name": k, "quantity": v} for k, v in groceries.items()]
    return jsonify(items)

if __name__ == "__main__":
    app.run(debug=True)
