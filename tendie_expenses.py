import os
import calendar
from datetime import datetime
from flask import request, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import convertSQLToDict

# DB setup
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def addExpenses(formData, userID):
    expenses = []
    expense = {"description": None, "category": None, "date": None, "amount": None, "payer": None}

    # One record (from index route)
    if "." not in formData[0][0]:
        for key, value in formData:
            expense[key] = value.strip()
        expense["amount"] = float(expense["amount"])
        expenses.append(expense)

    # Multiple records (from addexpenses route)
    else:
        counter = 0
        for key, value in formData:
            cleanKey = key.split(".")[0]
            expense[cleanKey] = value.strip()
            counter += 1
            if counter % 5 == 0:
                expense["amount"] = float(expense["amount"])
                expenses.append(expense.copy())

    # Insert into DB
    for expense in expenses:
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        db.execute("""
            INSERT INTO expenses (description, category, expenseDate, amount, payer, submitTime, user_id)
            VALUES (:description, :category, :expenseDate, :amount, :payer, :submitTime, :usersID)
        """, {
            "description": expense["description"],
            "category": expense["category"],
            "expenseDate": expense["date"],
            "amount": expense["amount"],
            "payer": expense["payer"],
            "submitTime": now,
            "usersID": userID
        })
    db.commit()

    # ✅ Alert Logic: Budget usage warning
    for expense in expenses:
        category = expense["category"]
        result = db.execute("""
            SELECT SUM(amount) FROM expenses
            WHERE user_id = :userID AND category = :category
        """, {"userID": userID, "category": category}).fetchone()

        current_spent = result[0] if result[0] else 0

        result = db.execute("""
            SELECT bc.amount FROM budgetCategories bc
            JOIN budgets b ON bc.budgets_id = b.id
            WHERE b.user_id = :userID AND bc.category_id = (
                SELECT id FROM categories WHERE name = :category LIMIT 1
            )
        """, {"userID": userID, "category": category}).fetchone()

        budget_limit = result[0] if result else None

        if budget_limit:
            usage_ratio = current_spent / budget_limit
            if usage_ratio > 1:
                flash(f"⚠️ You’ve exceeded your budget for '{category}'!", "danger")
            elif usage_ratio >= 0.5:
                flash(f"⚠️ You’ve used over 50% of your '{category}' budget.", "warning")

    return expenses


def getHistory(userID):
    results = db.execute("""
        SELECT description, category, expenseDate AS date, payer, amount, submitTime
        FROM expenses
        WHERE user_id = :usersID
        ORDER BY id ASC
    """, {"usersID": userID}).fetchall()

    return convertSQLToDict(results)


def getExpense(formData, userID):
    expense = {
        "description": formData.get("oldDescription").strip(),
        "category": formData.get("oldCategory").strip(),
        "date": formData.get("oldDate").strip(),
        "amount": float(formData.get("oldAmount").replace("$", "").replace(",", "").strip()),
        "payer": formData.get("oldPayer").strip(),
        "submitTime": formData.get("submitTime").strip(),
        "id": None
    }

    expenseID = db.execute("""
        SELECT id FROM expenses
        WHERE user_id = :usersID
        AND description = :oldDescription
        AND category = :oldCategory
        AND expenseDate = :oldDate
        AND amount = :oldAmount
        AND payer = :oldPayer
        AND submitTime = :oldSubmitTime
    """, {
        "usersID": userID,
        "oldDescription": expense["description"],
        "oldCategory": expense["category"],
        "oldDate": expense["date"],
        "oldAmount": expense["amount"],
        "oldPayer": expense["payer"],
        "oldSubmitTime": expense["submitTime"]
    }).fetchone()

    expense["id"] = expenseID[0] if expenseID else None
    return expense


def deleteExpense(expense, userID):
    result = db.execute("""
        DELETE FROM expenses
        WHERE user_id = :usersID AND id = :oldExpenseID
    """, {"usersID": userID, "oldExpenseID": expense["id"]})
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

    hasChanges = any(
        oldExpense.get(key) != expense.get(key)
        for key in ["description", "category", "date", "amount", "payer"]
    )

    if not hasChanges:
        return None

    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    result = db.execute("""
        UPDATE expenses SET
        description = :newDescription,
        category = :newCategory,
        expenseDate = :newDate,
        amount = :newAmount,
        payer = :newPayer,
        submitTime = :newSubmitTime
        WHERE id = :existingExpenseID AND user_id = :usersID
    """, {
        "newDescription": expense["description"],
        "newCategory": expense["category"],
        "newDate": expense["date"],
        "newAmount": expense["amount"],
        "newPayer": expense["payer"],
        "newSubmitTime": now,
        "existingExpenseID": oldExpense["id"],
        "usersID": userID
    }).rowcount
    db.commit()

    if result:
        return [expense]
    else:
        return None
