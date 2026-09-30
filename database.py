import sqlite3


DATABASE = "codearena.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    connection = get_db_connection()

    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Problems table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            topic TEXT NOT NULL
        )
    """)

    # Test cases table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            input_data TEXT NOT NULL,
            expected_output TEXT NOT NULL,
            FOREIGN KEY (problem_id) REFERENCES problems(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            problem_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            status TEXT NOT NULL,
            passed INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (problem_id) REFERENCES problems(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":

    # Create all tables
    init_db()

    connection = get_db_connection()

    # -----------------------------------
    # ADD PROBLEMS
    # -----------------------------------
        
    problems = [
        (
            "Reverse an Array",
            "Given an array of integers, reverse the array and return the result.",
            "Easy",
            "Arrays"
        ),
        (
            "Find Maximum Element",
            "Given an array of integers, find the largest element in the array.",
            "Easy",
            "Arrays"
        ),
        (
            "Check Palindrome",
            "Given a string, determine whether it is a palindrome.",
            "Easy",
            "Strings"
        ),
        (
            "Find Second Largest",
            "Given an array of integers, find the second largest element in the array.",
            "Easy",
            "Arrays"
        ),
        (
            "Count Vowels",
            "Given a string, count the number of vowels present in the string.",
            "Easy",
            "Strings"
        ),
        (
            "Two Sum",
            "Given an array of integers and a target value, find two numbers whose sum equals the target.",
            "Medium",
            "Arrays"
        ),
        (
            "Remove Duplicates",
            "Given a sorted array, remove duplicate elements and return the array containing only unique values.",
            "Easy",
            "Arrays"
        ),
        (
            "Check Prime Number",
            "Given an integer, determine whether the number is prime.",
            "Easy",
            "Mathematics"
        ),
        (
            "Binary Search",
            "Given a sorted array and a target value, find the index of the target using binary search. Return -1 if the target is not found.",
            "Medium",
            "Searching"
        ),
        (
            "Valid Parentheses",
            "Given a string containing parentheses, determine whether the parentheses are valid and properly matched.",
            "Medium",
            "Stack"
        )
    ]

    

    for problem in problems:

        existing = connection.execute(
            "SELECT id FROM problems WHERE title = ?",
            (problem[0],)
        ).fetchone()

        if not existing:

            connection.execute(
                """
                INSERT INTO problems
                (title, description, difficulty, topic)
                VALUES (?, ?, ?, ?)
                """,
                problem
            )

    connection.commit()

    # -----------------------------------
    # GET PROBLEM IDs
    # -----------------------------------

    reverse_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Reverse an Array",)
    ).fetchone()

    maximum_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Find Maximum Element",)
    ).fetchone()

    palindrome_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Check Palindrome",)
    ).fetchone()

    second_largest_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Find Second Largest",)
    ).fetchone()

    count_vowels_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Count Vowels",)
    ).fetchone()

    two_sum_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Two Sum",)
    ).fetchone()

    remove_duplicates_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Remove Duplicates",)
    ).fetchone()

    prime_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Check Prime Number",)
    ).fetchone()

    binary_search_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Binary Search",)
    ).fetchone()

    valid_parentheses_problem = connection.execute(
        "SELECT id FROM problems WHERE title = ?",
        ("Valid Parentheses",)
    ).fetchone()

    # -----------------------------------
    # ADD TEST CASES
    # -----------------------------------

    test_cases = [

        # Reverse an Array
        (
            reverse_problem["id"],
            "[1, 2, 3, 4, 5]",
            "[5, 4, 3, 2, 1]"
        ),

        (
            reverse_problem["id"],
            "[10, 20, 30]",
            "[30, 20, 10]"
        ),

        (
            reverse_problem["id"],
            "[7]",
            "[7]"
        ),

        # Find Maximum Element
        (
            maximum_problem["id"],
            "[4, 8, 2, 10, 6]",
            "10"
        ),

        (
            maximum_problem["id"],
            "[5, 1, 9, 3]",
            "9"
        ),

        # Check Palindrome
        (
            palindrome_problem["id"],
            "\"madam\"",
            "True"
        ),

        (
            palindrome_problem["id"],
            "\"hello\"",
            "False"
        ),

                # Find Second Largest
        (
            second_largest_problem["id"],
            "[10, 5, 8, 20, 15]",
            "15"
        ),

        (
            second_largest_problem["id"],
            "[4, 9, 2, 7]",
            "7"
        ),

        # Count Vowels
        (
            count_vowels_problem["id"],
            "\"hello\"",
            "2"
        ),

        (
            count_vowels_problem["id"],
            "\"education\"",
            "5"
        ),

        # Two Sum
        (
            two_sum_problem["id"],
            "([2, 7, 11, 15], 9)",
            "[0, 1]"
        ),

        (
            two_sum_problem["id"],
            "([3, 2, 4], 6)",
            "[1, 2]"
        ),

        # Remove Duplicates
        (
            remove_duplicates_problem["id"],
            "[1, 1, 2, 2, 3, 3]",
            "[1, 2, 3]"
        ),

        (
            remove_duplicates_problem["id"],
            "[1, 1, 1, 2, 3]",
            "[1, 2, 3]"
        ),

        # Check Prime Number
        (
            prime_problem["id"],
            "7",
            "true"
        ),

        (
            prime_problem["id"],
            "10",
            "false"
        ),

        # Binary Search
        (
            binary_search_problem["id"],
            "([1, 3, 5, 7, 9], 7)",
            "3"
        ),

        (
            binary_search_problem["id"],
            "([2, 4, 6, 8], 5)",
            "-1"
        ),

        # Valid Parentheses
        (
            valid_parentheses_problem["id"],
            "\"()[]{}\"",
            "true"
        ),

        (
            valid_parentheses_problem["id"],
            "\"([)]\"",
            "false"
        )

    ]

    for test_case in test_cases:

        existing = connection.execute(
            """
            SELECT id
            FROM test_cases
            WHERE problem_id = ?
            AND input_data = ?
            """,
            (
                test_case[0],
                test_case[1]
            )
        ).fetchone()

        if existing:

            connection.execute(
                """
                UPDATE test_cases
                SET expected_output = ?
                WHERE id = ?
                """,
                (
                    test_case[2],
                    existing["id"]
                )
            )

        else:

            connection.execute(
                """
                INSERT INTO test_cases
                (problem_id, input_data, expected_output)
                VALUES (?, ?, ?)
                """,
                test_case
            )
    connection.commit()
    connection.close()

    print("Database initialized successfully!")