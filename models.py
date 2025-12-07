from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

db = SQLAlchemy()

planner_table = Table(
    "planner",
    db.metadata,
    Column("day", String, primary_key=True),
    Column("meal_id", Integer, ForeignKey("meals.id"), primary_key=True),
)


class Meal(db.Model):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    image = Column(String)
    ingredients = Column(Text)
    instructions = Column(Text)

    favorites = relationship("Favorite", back_populates="meal")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey("meals.id"))

    meal = relationship("Meal", back_populates="favorites")

    def to_dict(self):
        return {
            "id": self.id,
            "meal_id": self.meal_id,
        }
