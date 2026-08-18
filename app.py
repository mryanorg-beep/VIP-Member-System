from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
import io
import csv
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = "vip-secret-key"

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"


def get_connection():

    conn = sqlite3.connect("members.db")

    conn.row_factory = sqlite3.Row

    return conn


def get_members(search="", level="", sort=""):

    conn = get_connection()

    cursor = conn.cursor()

    query = "SELECT * FROM members WHERE 1=1"

    params = []

    if search:

        query += """
        AND (
            name LIKE ?
            OR member_id LIKE ?
            OR code LIKE ?
        )
        """

        params.extend([
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ])

    if level:

        query += " AND level=?"

        params.append(level)

    if sort == "income":

        query += " ORDER BY CAST(income AS INTEGER) DESC"

    elif sort == "withdrawal":

        query += " ORDER BY CAST(withdrawal AS INTEGER) DESC"

    elif sort == "tasks":

        query += " ORDER BY CAST(tasks AS INTEGER) DESC"

    else:

        query += " ORDER BY rank ASC"

    cursor.execute(query, params)

    members = cursor.fetchall()

    conn.close()

    return members


@app.route("/")
def home():

    members = get_members()

    return render_template(
        "index.html",
        members=members
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/admin")

        return "Login Failed"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/admin")
def admin():

    if "admin" not in session:

        return redirect("/login")

    search = request.args.get(
        "search",
        ""
    )

    level = request.args.get(
        "level",
        ""
    )

    sort = request.args.get(
        "sort",
        ""
    )

    members = get_members(
        search,
        level,
        sort
    )

    return render_template(
        "admin.html",
        members=members
    )


@app.route("/add", methods=["POST"])
def add_member():

    if "admin" not in session:

        return redirect("/login")

    filename = ""

    if "photo" in request.files:

        file = request.files["photo"]

        if file.filename:

            filename = secure_filename(
                file.filename
            )

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO members
        (
            rank,
            name,
            member_id,
            code,
            level,
            income,
            withdrawal,
            payment,
            tasks,
            status,
            photo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.form["rank"],
            request.form["name"],
            request.form["member_id"],
            request.form["code"],
            request.form["level"],
            request.form["income"],
            request.form["withdrawal"],
            request.form["payment"],
            request.form["tasks"],
            request.form["status"],
            filename
        )
    )

    conn.commit()

    conn.close()

    return redirect("/admin")


@app.route("/edit/<int:id>", methods=["POST"])
def edit_member(id):

    if "admin" not in session:

        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE members SET

        name=?,
        member_id=?,
        code=?,
        level=?,
        income=?,
        withdrawal=?,
        payment=?,
        tasks=?,
        status=?

        WHERE id=?
        """,
        (
            request.form["name"],
            request.form["member_id"],
            request.form["code"],
            request.form["level"],
            request.form["income"],
            request.form["withdrawal"],
            request.form["payment"],
            request.form["tasks"],
            request.form["status"],
            id
        )
    )

    conn.commit()

    conn.close()

    return redirect("/admin")


@app.route("/delete/<int:id>")
def delete_member(id):

    if "admin" not in session:

        return redirect("/login")

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM members WHERE id=?",
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect("/admin")


@app.route("/export")
def export_members():

    if "admin" not in session:

        return redirect("/login")

    search = request.args.get(
        "search",
        ""
    )

    level = request.args.get(
        "level",
        ""
    )

    sort = request.args.get(
        "sort",
        ""
    )

    members = get_members(
        search,
        level,
        sort
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Rank",
        "Name",
        "Member ID",
        "Code",
        "VIP Level",
        "Income",
        "Withdrawal",
        "Payment",
        "Tasks",
        "Status"
    ])

    for member in members:

        writer.writerow([
            member["rank"],
            member["name"],
            member["member_id"],
            member["code"],
            member["level"],
            member["income"],
            member["withdrawal"],
            member["payment"],
            member["tasks"],
            member["status"]
        ])

    output.seek(0)

    data = io.BytesIO()

    data.write(
        output.getvalue().encode("utf-8-sig")
    )

    data.seek(0)

    return send_file(
        data,
        mimetype="text/csv",
        as_attachment=True,
        download_name="VIP_Members.csv"
    )


if __name__ == "__main__":

    app.run(debug=True)