from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "created_at": self.created_at.isoformat()
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meal = db.relationship("Meal", backref="favorites")

    def to_dict(self):
        return {
            "id": self.id,
            "meal_id": self.meal_id,
            "created_at": self.created_at.isoformat()
        }
