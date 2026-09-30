from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import sqlite3
import subprocess
import tempfile
import os
import ast
import json


import shutil


def execute_java(code, input_value=None):
    """
    Compile and run Java code.

    If input_value is provided, pass it to the
    Java program through standard input.
    """

    if not shutil.which("java") or not shutil.which("javac"):
        return {
            "success": False,
            "error": "Java JDK is not installed or is not in PATH."
        }

    # Each execution gets its own temporary directory.
    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = os.path.join(temp_dir, "Main.java")

        with open(source_path, "w", encoding="utf-8") as file:
            file.write(code)

        # Compile Java source.
        try:
            compile_result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "Main.java"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Java compilation timed out."
            }

        if compile_result.returncode != 0:
            return {
                "success": False,
                "error": compile_result.stderr,
                "stage": "compilation"
            }

        # Run the compiled program.
        try:
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, "Main"],
                cwd=temp_dir,
                input=input_value if input_value is not None else "\n",
                capture_output=True,
                text=True,
                timeout=5
            )

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Java execution timed out.",
                "stage": "execution"
            }

        if run_result.returncode != 0:
            return {
                "success": False,
                "error": run_result.stderr,
                "stage": "execution"
            }

        return {
            "success": True,
            "output": run_result.stdout
        }

app = Flask(__name__)

# Secret key for sessions
app.secret_key = "codearena-secret-key"


@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
                """,
                (username, email, hashed_password)
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()
            return "Username or email already exists. Please use a different one."

        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        return "Invalid username or password."

    return render_template("login.html")

@app.route("/problem/<int:problem_id>")
def problem(problem_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    problem_data = connection.execute(
        "SELECT * FROM problems WHERE id = ?",
        (problem_id,)
    ).fetchone()

    connection.close()

    if problem_data is None:
        return "Problem not found", 404

    return render_template(
        "problem.html",
        problem=problem_data
    )

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    problems = connection.execute(
        "SELECT * FROM problems ORDER BY id"
    ).fetchall()

    total_problems = len(problems)

    stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_submissions,
            SUM(CASE WHEN status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_submissions,
            COUNT(DISTINCT CASE WHEN status = 'Accepted' THEN problem_id END) AS problems_solved
        FROM submissions
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # IDs of problems this user has solved at least once.
    solved_rows = connection.execute(
        """
        SELECT DISTINCT problem_id
        FROM submissions
        WHERE user_id = ? AND status = 'Accepted'
        """,
        (session["user_id"],)
    ).fetchall()
    solved_problem_ids = {row["problem_id"] for row in solved_rows}

    connection.close()

    total_submissions = stats["total_submissions"] or 0
    accepted_submissions = stats["accepted_submissions"] or 0
    problems_solved = stats["problems_solved"] or 0

    if total_submissions > 0:
        success_rate = round(
            (accepted_submissions / total_submissions) * 100,
            1
        )
    else:
        success_rate = 0

    progress_percentage = (
        round((problems_solved / total_problems) * 100)
        if total_problems > 0
        else 0
    )

    total_problems=total_problems,
    progress_percentage=progress_percentage

    return render_template(
        "dashboard.html",
        username=session["username"],
        problems=problems,
        total_submissions=total_submissions,
        accepted_submissions=accepted_submissions,
        problems_solved=problems_solved,
        success_rate=success_rate,
        solved_problem_ids=solved_problem_ids
    )

@app.route("/run-code", methods=["POST"])
def run_code():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "You must be logged in."
        }), 401

    data = request.get_json()

    code = data.get("code", "")
    language = data.get("language", "python")
    custom_input = data.get("custom_input", "")

    # Run Java code when Java is selected
    if language == "java":
        if not code.strip():
            return jsonify({
                "success": False,
                "error": "Please write some Java code first."
            }), 400

        return jsonify(execute_java(code, custom_input + "\n"))

    # Only Python and Java are supported
    if language != "python":
        return jsonify({
            "success": False,
            "error": "Unsupported programming language."
        }), 400

    # Execute Java when Java is selected
    if language == "java":
        if not code.strip():
            return jsonify({
                "success": False,
                "error": "Please write some Java code first."
            }), 400

        return jsonify(execute_java(code))

        # Reject unknown languages
    if language != "python":
        return jsonify({
            "success": False,
            "error": "Unsupported programming language."
        }), 400
    
        if not code.strip():
            return jsonify({
                "success": False,
                "error": "No code provided."
            }), 400

    temp_file = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as file:

            file.write(code)
            temp_file = file.name

        result = subprocess.run(
            ["python", temp_file],
            input=custom_input,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:

            return jsonify({
                "success": True,
                "output": result.stdout
            })

        return jsonify({
            "success": False,
            "error": result.stderr
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "error": "Execution timed out. Your code took too long."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        })

    finally:

        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

def save_submission(user_id, problem_id, code, status, passed, total):
    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO submissions
        (user_id, problem_id, code, status, passed, total)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, problem_id, code, status, passed, total)
    )

    connection.commit()
    connection.close()


@app.route("/submit", methods=["POST"])
def submit():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "You must be logged in."
        }), 401

    data = request.get_json()

    code = data.get("code", "")
    problem_id = data.get("problem_id")

    if not code.strip():
        return jsonify({
            "success": False,
            "error": "Please write some code first."
        }), 400

    connection = get_db_connection()

    test_cases = connection.execute(
        """
        SELECT input_data, expected_output
        FROM test_cases
        WHERE problem_id = ?
        ORDER BY id
        """,
        (problem_id,)
    ).fetchall()

    connection.close()

    if not test_cases:
        return jsonify({
            "success": False,
            "error": "No test cases found for this problem."
        }), 404

    passed = 0
    total = len(test_cases)

    
    # Java submission judging
    language = data.get("language", "python")

    if language == "java":

        for test_case in test_cases:

            # Read the existing database test case
            input_value = ast.literal_eval(
                test_case["input_data"]
            )

            try:
                expected_value = json.loads(
                    test_case["expected_output"]
                )
            except (json.JSONDecodeError, TypeError):
                expected_value = ast.literal_eval(
                    test_case["expected_output"]
                )

            # Java receives one JSON input line through System.in
            java_input = json.dumps(input_value) + "\n"

            result = execute_java(code, java_input)

            if not result["success"]:

                error_message = result.get(
                    "error", "Java execution failed."
                )

                if result.get("stage") == "compilation":
                    status = "Compilation Error"
                elif "timed out" in error_message.lower():
                    status = "Time Limit Exceeded"
                else:
                    status = "Runtime Error"

                save_submission(
                    session["user_id"],
                    problem_id,
                    code,
                    status,
                    passed,
                    total
                )

                return jsonify({
                    "success": False,
                    "status": status,
                    "passed": passed,
                    "total": total,
                    "error": error_message
                })

            # Java must print its answer as JSON
            try:
                actual_output = json.loads(
                    result["output"].strip()
                )
            except json.JSONDecodeError:

                status = "Runtime Error"

                save_submission(
                    session["user_id"],
                    problem_id,
                    code,
                    status,
                    passed,
                    total
                )

                return jsonify({
                    "success": False,
                    "status": status,
                    "passed": passed,
                    "total": total,
                    "error": (
                        "Invalid output. Print only the answer "
                        "in JSON format."
                    )
                })

            if actual_output != expected_value:

                status = "Wrong Answer"

                save_submission(
                    session["user_id"],
                    problem_id,
                    code,
                    status,
                    passed,
                    total
                )

                return jsonify({
                    "success": True,
                    "status": status,
                    "passed": passed,
                    "total": total
                })

            passed += 1

        status = "Accepted"

        save_submission(
            session["user_id"],
            problem_id,
            code,
            status,
            passed,
            total
        )

        return jsonify({
            "success": True,
            "status": status,
            "passed": passed,
            "total": total
        })

    if language != "python":
        return jsonify({
            "success": False,
            "error": "Unsupported programming language."
        }), 400

    temp_file = None

    try:

        for test_case in test_cases:

            input_value = ast.literal_eval(
                test_case["input_data"]
            )

            try:
                expected_value = json.loads(test_case["expected_output"])
            except (json.JSONDecodeError, TypeError):
                expected_value = ast.literal_eval(test_case["expected_output"])

            runner_code = f"""
{code}

import json

result = solve({repr(input_value)})

print(json.dumps(result))
"""

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False
            ) as file:

                file.write(runner_code)
                temp_file = file.name

            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )

            os.remove(temp_file)
            temp_file = None

            # Runtime error
            if result.returncode != 0:

                status = "Runtime Error"

                save_submission(
                    session["user_id"],
                    problem_id,
                    code,
                    status,
                    passed,
                    total
                )

                return jsonify({
                    "success": False,
                    "status": status,
                    "passed": passed,
                    "total": total,
                    "error": result.stderr
                })

            actual_output = json.loads(
                result.stdout.strip()
            )

            # Wrong answer
            if actual_output != expected_value:

                status = "Wrong Answer"

                save_submission(
                    session["user_id"],
                    problem_id,
                    code,
                    status,
                    passed,
                    total
                )

                return jsonify({
                    "success": True,
                    "status": status,
                    "passed": passed,
                    "total": total
                })

            passed += 1

        # All tests passed
        status = "Accepted"

        save_submission(
            session["user_id"],
            problem_id,
            code,
            status,
            passed,
            total
        )

        return jsonify({
            "success": True,
            "status": status,
            "passed": passed,
            "total": total
        })

    except subprocess.TimeoutExpired:

        status = "Time Limit Exceeded"

        save_submission(
            session["user_id"],
            problem_id,
            code,
            status,
            passed,
            total
        )

        return jsonify({
            "success": False,
            "status": status,
            "passed": passed,
            "total": total
        })

    except Exception as error:

        status = "Error"

        save_submission(
            session["user_id"],
            problem_id,
            code,
            status,
            passed,
            total
        )

        return jsonify({
            "success": False,
            "status": status,
            "error": str(error)
        })

    finally:

        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


@app.route("/submissions")
def submissions():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    submissions_data = connection.execute(
        """
        SELECT
            submissions.id,
            problems.title,
            submissions.status,
            submissions.passed,
            submissions.total,
            submissions.created_at
        FROM submissions
        JOIN problems
            ON submissions.problem_id = problems.id
        WHERE submissions.user_id = ?
        ORDER BY submissions.created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "submissions.html",
        submissions=submissions_data
    )

@app.route("/submission/<int:submission_id>")
def submission_details(submission_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    submission = connection.execute(
        """
        SELECT
            submissions.id,
            submissions.code,
            submissions.status,
            submissions.passed,
            submissions.total,
            submissions.created_at,
            problems.title,
            problems.description,
            problems.difficulty,
            problems.topic
        FROM submissions
        JOIN problems
            ON submissions.problem_id = problems.id
        WHERE submissions.id = ?
        AND submissions.user_id = ?
        """,
        (submission_id, session["user_id"])
    ).fetchone()

    connection.close()

    if submission is None:
        return "Submission not found", 404

    return render_template(
        "submission_details.html",
        submission=submission
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)