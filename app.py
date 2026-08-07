from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os


# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "expense.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + DATABASE_PATH
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==========================================
# EXPENSE MODEL
# ==========================================

class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    date = db.Column(
        db.String(20),
        nullable=False
    )


# ==========================================
# HOME / DASHBOARD
# ==========================================

@app.route("/")
def home():

    # Get filter values
    search = request.args.get(
        "search",
        ""
    )

    category = request.args.get(
        "category",
        ""
    )

    from_date = request.args.get(
        "from_date",
        ""
    )

    to_date = request.args.get(
        "to_date",
        ""
    )


    # Start query
    query = Expense.query


    # Search by title
    if search:

        query = query.filter(
            Expense.title.ilike(
                f"%{search}%"
            )
        )


    # Filter by category
    if category:

        query = query.filter(
            Expense.category == category
        )


    # Filter by starting date
    if from_date:

        query = query.filter(
            Expense.date >= from_date
        )


    # Filter by ending date
    if to_date:

        query = query.filter(
            Expense.date <= to_date
        )


    # Get filtered expenses
    expenses = query.order_by(
        Expense.date.desc()
    ).all()


    # ==========================================
    # STATISTICS
    # ==========================================

    # Total expense
    total_expense = sum(
        expense.amount
        for expense in expenses
    )


    # Number of expenses
    total_records = len(expenses)


    # Average expense
    average_expense = (

        total_expense / total_records

        if total_records > 0

        else 0

    )


    # ==========================================
    # CATEGORY STATISTICS
    # ==========================================

    expense_ids = [
        expense.id
        for expense in expenses
    ]


    if expense_ids:

        category_data = (

            db.session.query(
                Expense.category,
                func.sum(Expense.amount)
            )

            .filter(
                Expense.id.in_(expense_ids)
            )

            .group_by(
                Expense.category
            )

            .all()

        )

    else:

        category_data = []


    # ==========================================
    # DATA FOR CHART.JS
    # ==========================================

    category_labels = [

        category_name

        for category_name, amount
        in category_data

    ]


    category_amounts = [

        float(amount)

        for category_name, amount
        in category_data

    ]


    # ==========================================
    # SEND DATA TO HTML
    # ==========================================

    return render_template(

        "index.html",

        expenses=expenses,

        total_expense=total_expense,

        total_records=total_records,

        average_expense=average_expense,

        category_data=category_data,

        category_labels=category_labels,

        category_amounts=category_amounts,

        search=search,

        category=category,

        from_date=from_date,

        to_date=to_date

    )


# ==========================================
# ADD EXPENSE
# ==========================================

@app.route(
    "/add",
    methods=["POST"]
)
def add_expense():

    title = request.form["title"]

    amount = request.form["amount"]

    category = request.form["category"]

    date = request.form["date"]


    expense = Expense(

        title=title,

        amount=float(amount),

        category=category,

        date=date

    )


    db.session.add(expense)

    db.session.commit()


    return redirect(
        url_for("home")
    )


# ==========================================
# EDIT EXPENSE
# ==========================================

@app.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit_expense(id):

    expense = Expense.query.get_or_404(id)


    if request.method == "POST":

        expense.title = request.form[
            "title"
        ]

        expense.amount = float(
            request.form["amount"]
        )

        expense.category = request.form[
            "category"
        ]

        expense.date = request.form[
            "date"
        ]


        db.session.commit()


        return redirect(
            url_for("home")
        )


    return render_template(

        "edit.html",

        expense=expense

    )


# ==========================================
# DELETE EXPENSE
# ==========================================

@app.route(
    "/delete/<int:id>"
)
def delete_expense(id):

    expense = Expense.query.get_or_404(id)


    db.session.delete(expense)

    db.session.commit()


    return redirect(
        url_for("home")
    )


# ==========================================
# CREATE DATABASE
# ==========================================

with app.app_context():

    os.makedirs(
        os.path.dirname(DATABASE_PATH),
        exist_ok=True
    )

    db.create_all()


# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )