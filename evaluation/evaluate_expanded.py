import json
import math
import time
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from app.agent.loop import run_agent


GROUND_TRUTH_PATH = (
    Path(__file__).parent
    / "questions_expanded.json"
)

ABS_TOLERANCE = 0.005
REL_TOLERANCE = 1e-9


def is_numeric(value):
    return isinstance(
        value,
        (int, float, Decimal),
    ) and not isinstance(
        value,
        bool,
    )


def values_equal(actual, expected):

    if is_numeric(actual) and is_numeric(expected):

        return math.isclose(
            float(actual),
            float(expected),
            abs_tol=ABS_TOLERANCE,
            rel_tol=REL_TOLERANCE,
        )

    return actual == expected


def normalize_dimension_value(
    column,
    value,
):
    """
    Normalize database date/time representations
    to the benchmark's canonical dimension format.

    This only applies to known temporal dimensions.
    """

    if column == "month":

        if isinstance(
            value,
            (datetime, date),
        ):
            return value.strftime("%Y-%m")

        if isinstance(value, str):

            value = value.strip()

            if len(value) >= 7:
                return value[:7]

        return value

    if column == "quarter":

        if isinstance(
            value,
            (datetime, date),
        ):
            quarter = (
                (value.month - 1) // 3
            ) + 1

            return f"Q{quarter}"

        if is_numeric(value):

            quarter = int(value)

            if 1 <= quarter <= 4:
                return f"Q{quarter}"

            return value

        if isinstance(value, str):

            value = value.strip().upper()

            if value.isdigit():

                quarter = int(value)

                if 1 <= quarter <= 4:
                    return f"Q{quarter}"

            if value.startswith("Q"):

                return value

        return value

    return value


def normalize_value(
    column,
    value,
):

    value = normalize_dimension_value(
        column=column,
        value=value,
    )

    if isinstance(value, str):

        value = value.strip()

        if value.startswith("Q"):
            return value.upper()

    return value


def rows_equal(
    actual_rows,
    expected_rows,
    columns,
):

    if len(actual_rows) != len(expected_rows):
        return False

    unmatched = list(expected_rows)

    for actual_row in actual_rows:

        found_index = None

        for index, expected_row in enumerate(
            unmatched
        ):

            if len(actual_row) != len(expected_row):
                continue

            matches = all(
                values_equal(
                    normalize_value(
                        column=column,
                        value=actual,
                    ),
                    normalize_value(
                        column=column,
                        value=expected,
                    ),
                )
                for column, actual, expected
                in zip(
                    columns,
                    actual_row,
                    expected_row,
                )
            )

            if matches:
                found_index = index
                break

        if found_index is None:
            return False

        unmatched.pop(found_index)

    return not unmatched


def columns_compatible(
    actual_columns,
    expected_columns,
):

    return len(actual_columns) == len(
        expected_columns
    )


def evaluate_question(question_data):

    question = question_data["question"]

    expected_columns = question_data[
        "expected_columns"
    ]

    expected_rows = question_data[
        "expected_rows"
    ]

    start_time = time.perf_counter()

    try:

        state = run_agent(question)

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        actual_columns = state.columns
        actual_rows = state.rows

        column_match = columns_compatible(
            actual_columns,
            expected_columns,
        )

        row_match = rows_equal(
            actual_rows,
            expected_rows,
            actual_columns,
        )

        passed = (
            column_match
            and row_match
        )

        return {
            "question": question,
            "passed": passed,
            "columns_match": column_match,
            "rows_match": row_match,
            "actual_columns": actual_columns,
            "expected_columns": expected_columns,
            "actual_rows": actual_rows,
            "expected_rows": expected_rows,
            "sql_retries": (
                state.trace.sql_retries
                if state.trace
                else 0
            ),
            "duration_ms": duration_ms,
            "sql": state.sql,
            "error": state.error,
        }

    except Exception as error:

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        return {
            "question": question,
            "passed": False,
            "columns_match": False,
            "rows_match": False,
            "actual_columns": [],
            "expected_columns": expected_columns,
            "actual_rows": [],
            "expected_rows": expected_rows,
            "sql_retries": 0,
            "duration_ms": duration_ms,
            "sql": "",
            "error": str(error),
        }


def print_result(
    index,
    result,
):

    status = (
        "PASS"
        if result["passed"]
        else "FAIL"
    )

    print(
        f"\n[{status}] Question {index}"
    )

    print(
        f"Question: {result['question']}"
    )

    print(
        f"Columns compatible: "
        f"{result['columns_match']}"
    )

    print(
        f"Result match: "
        f"{result['rows_match']}"
    )

    print(
        f"SQL retries: "
        f"{result['sql_retries']}"
    )

    print(
        f"Duration: "
        f"{result['duration_ms']:.2f} ms"
    )

    if not result["passed"]:

        print("\nEXPECTED COLUMNS")
        print("-" * 70)
        print(result["expected_columns"])

        print("\nACTUAL COLUMNS")
        print("-" * 70)
        print(result["actual_columns"])

        print("\nEXPECTED ROWS")
        print("-" * 70)

        for row in result["expected_rows"]:
            print(row)

        print("\nACTUAL ROWS")
        print("-" * 70)

        for row in result["actual_rows"]:
            print(row)

        print("\nGENERATED SQL")
        print("-" * 70)
        print(result["sql"])

        if result["error"]:

            print("\nERROR")
            print("-" * 70)
            print(result["error"])


def main():

    print("=" * 70)
    print("EXPANDED AI DATA ANALYST EVALUATION")
    print("=" * 70)

    with open(
        GROUND_TRUTH_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        questions = json.load(file)

    results = []

    for index, question_data in enumerate(
        questions,
        start=13,
    ):

        result = evaluate_question(
            question_data
        )

        results.append(result)

        print_result(
            index,
            result,
        )

    total = len(results)

    passed = sum(
        result["passed"]
        for result in results
    )

    failed = total - passed

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    average_latency = (
        sum(
            result["duration_ms"]
            for result in results
        )
        / total
        if total
        else 0
    )

    total_retries = sum(
        result["sql_retries"]
        for result in results
    )

    print("\n" + "=" * 70)
    print("EXPANDED EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Total questions : {total}"
    )

    print(
        f"Passed          : {passed}"
    )

    print(
        f"Failed          : {failed}"
    )

    print(
        f"Accuracy        : {accuracy:.2f}%"
    )

    print(
        f"Average latency : "
        f"{average_latency:.2f} ms"
    )

    print(
        f"SQL retries     : "
        f"{total_retries}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
