from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(50), nullable=False)

    date = db.Column(db.String(20), nullable=False)