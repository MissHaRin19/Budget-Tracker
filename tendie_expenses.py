import os
import calendar
from flask import flash
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict

# Create engine object to manage connections to DB
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def addExpenses(formData, userID):
    expenses = []
    expense = {"description": None, "category": None, "date": None, "amount": None, "payer": None}

    if "." not in formData[0][0]:
        for key, value in formData:
            expense[key] = value.strip()
        expense["amount"] = float(expense["amount"])
        expenses.append(expense)
    else:
        counter = 0
        for key, value in formData:
            cleanKey = key.split(".")
            expense[cleanKey[0]] = value.strip()
            counter += 1
            if counter % 5 == 0:
                expense["amount"] = float(expense["amount"])
                expenses.append(expense.copy())

    for expense in expenses:
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        # Get total spent in the category for this user
        current_spent = db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = :userID AND category = :category",
            {"userID": userID, "category": expense["category"]}
        ).fetchone()[0]

        # Get budget limit for this user in this category (optional: make this dynamic if using category-specific budgets)
        budget_limit = db.execute(
            """SELECT amount FROM budgets WHERE user_id = :userID ORDER BY id DESC LIMIT 1""",
            {"userID": userID}
        ).fetchone()

        if budget_limit:
            budget_limit = float(budget_limit[0])
            if current_spent + expense["amount"] > budget_limit:
                flash("⚠️ You’ve exceeded your budget for this category!", "danger")
            elif current_spent + expense["amount"] >= 0.9 * budget_limit:
                flash("⚠️ You're about to exceed your budget!", "warning")

        db.execute("""INSERT INTO expenses 
            (description, category, expenseDate, amount, payer, submitTime, user_id) 
            VALUES (:description, :category, :expenseDate, :amount, :payer, :submitTime, :usersID)""",
            {
                "description": expense["description"],
                "category": expense["category"],
                "expenseDate": expense["date"],
                "amount": expense["amount"],
                "payer": expense["payer"],
                "submitTime": now,
                "usersID": userID
            }
        )
    db.commit()
    return expenses


def getHistory(userID):
    results = db.execute(
        "SELECT description, category, expenseDate AS date, payer, amount, submitTime FROM expenses WHERE user_id = :usersID ORDER BY id ASC",
        {"usersID": userID}
    ).fetchall()
    return convertSQLToDict(results)


def getExpense(formData, userID):
    expense = {
        "description": formData.get("oldDescription").strip(),
        "category": formData.get("oldCategory").strip(),
        "date": formData.get("oldDate").strip(),
        "amount": float(formData.get("oldAmount").replace("$", "").replace(",", "")),
        "payer": formData.get("oldPayer").strip(),
        "submitTime": formData.get("submitTime").strip(),
        "id": None
    }

    expenseID = db.execute(
        "SELECT id FROM expenses WHERE user_id = :usersID AND description = :oldDescription AND category = :oldCategory AND expenseDate = :oldDate AND amount = :oldAmount AND payer = :oldPayer AND submitTime = :oldSubmitTime",
        {
            "usersID": userID,
            "oldDescription": expense["description"],
            "oldCategory": expense["category"],
            "oldDate": expense["date"],
            "oldAmount": expense["amount"],
            "oldPayer": expense["payer"],
            "oldSubmitTime": expense["submitTime"]
        }
    ).fetchone()

    if expenseID:
        expense["id"] = expenseID[0]
    return expense


def deleteExpense(expense, userID):
    result = db.execute("DELETE FROM expenses WHERE user_id = :usersID AND id = :oldExpenseID",
                        {"usersID": userID, "oldExpenseID": expense["id"]})
    db.commit()
    return result


def updateExpense(oldExpense, formData, userID):
    expense = {
        "description": formData.get("description").strip(),
        "category": formData.get("category").strip(),
        "date": formData.get("date").strip(),
        "amount": float(formData.get("amount").strip()),
        "payer": formData.get("payer").strip()
    }

    hasChanges = any(oldExpense[k] != expense[k] for k in ["description", "category", "date", "amount", "payer"])
    if not hasChanges:
        return None

    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    result = db.execute(
        """UPDATE expenses SET description = :newDescription, category = :newCategory, 
        expenseDate = :newDate, amount = :newAmount, payer = :newPayer, submitTime = :newSubmitTime 
        WHERE id = :existingExpenseID AND user_id = :usersID""",
        {
            "newDescription": expense["description"],
            "newCategory": expense["category"],
            "newDate": expense["date"],
            "newAmount": expense["amount"],
            "newPayer": expense["payer"],
            "newSubmitTime": now,
            "existingExpenseID": oldExpense["id"],
            "usersID": userID
        }
    ).rowcount
    db.commit()

    if result:
        return [expense]
    else:
        return None

