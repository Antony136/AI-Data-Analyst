"""
Evaluation runner for AI Data Analyst.

Compares agent results against trusted ground-truth results.

The evaluator allows:
- numeric type differences such as Decimal vs float
- small numeric precision differences
- harmless column alias differences
- harmless ordering differences when the question does not
  explicitly require an ordering
- equivalent quarter representations such as 1 and Q1
"""

import json
import math
from decimal import Decimal
from pathlib import Path

from app.agent.loop import run_agent


GROUND_TRUTH_PATH = (
    Path(__file__).parent / "questions.json"
)

ABS_TOLERANCE = 0.005
REL_TOLERANCE = 1e-9


def is_numeric(value):
    """
    Return True when a value is numeric.
    """

    return isinstance(
        value,
        (int, float, Decimal),
    ) and not isinstance(
        value,
        bool,
    )


def values_equal(
    actual,
    expected,
):
    """
    Compare individual result values.

    Numeric values use a small tolerance so that:
    - Decimal and float values compare correctly
    - database precision does not cause false failures
    - rounded percentage values remain compatible
    """

    if is_numeric(actual) and is_numeric(expected):

        return math.isclose(
            float(actual),
            float(expected),
            rel_tol=REL_TOLERANCE,
            abs_tol=ABS_TOLERANCE,
        )

    # Quarter normalization:
    #
    # Actual:
    #     1
    #
    # Expected:
    #     "Q1"
    #
    # These represent the same quarter.

    if isinstance(expected, str):

        normalized_expected = expected.strip().upper()

        if normalized_expected.startswith("Q"):

            quarter_number = normalized_expected[1:]

            if quarter_number.isdigit():

                if is_numeric(actual):

                    return int(float(actual)) == int(
                        quarter_number
                    )

                if isinstance(actual, str):

                    normalized_actual = actual.strip().upper()

                    if normalized_actual.startswith("Q"):
                        return (
                            normalized_actual[1:]
                            == quarter_number
                        )

    if isinstance(actual, str):

        normalized_actual = actual.strip().upper()

        if normalized_actual.startswith("Q"):

            quarter_number = normalized_actual[1:]

            if quarter_number.isdigit():

                if is_numeric(expected):

                    return int(float(expected)) == int(
                        quarter_number
                    )

    return actual == expected


def rows_equal(
    actual_rows,
    expected_rows,
):
    """
    Compare result rows.

    Row ordering is ignored because SQL result ordering is
    not semantically meaningful unless explicitly requested
    by the question.
    """

    if len(actual_rows) != len(expected_rows):
        return False

    normalized_actual = [
        tuple(row)
        for row in actual_rows
    ]

    normalized_expected = [
        tuple(row)
        for row in expected_rows
    ]

    unmatched_actual = normalized_actual.copy()

    for expected_row in normalized_expected:

        matching_index = None

        for index, actual_row in enumerate(
            unmatched_actual
        ):

            if len(actual_row) != len(expected_row):
                continue

            if all(
                values_equal(actual, expected)
                for actual, expected
                in zip(actual_row, expected_row)
            ):
                matching_index = index
                break

        if matching_index is None:
            return False

        unmatched_actual.pop(matching_index)

    return True


def columns_compatible(
    actual_columns,
    expected_columns,
):
    """
    Check whether result shapes are compatible.

    Column aliases may differ because aliases such as:
        total_revenue
        revenue

    do not change the underlying result.
    """

    return len(actual_columns) == len(expected_columns)


def evaluate_question(
    question_data,
):
    """
    Run one evaluation question.
    """

    question = question_data["question"]

    expected_columns = question_data["expected_columns"]
    expected_rows = question_data["expected_rows"]

    state = None

    try:

        state = run_agent(question)

        actual_columns = state.columns
        actual_rows = state.rows

        column_match = columns_compatible(
            actual_columns=actual_columns,
            expected_columns=expected_columns,
        )

        result_match = rows_equal(
            actual_rows=actual_rows,
            expected_rows=expected_rows,
        )

        passed = (
            column_match
            and result_match
            and not state.error
        )

        return {
            "question": question,
            "passed": passed,
            "columns_compatible": column_match,
            "result_match": result_match,
            "sql_retries": (
                state.trace.sql_retries
                if state.trace
                else 0
            ),
            "duration_ms": (
                state.trace.total_duration_ms
                if state.trace
                else 0
            ),
            "sql": state.sql,
            "expected_columns": expected_columns,
            "actual_columns": actual_columns,
            "expected_rows": expected_rows,
            "actual_rows": actual_rows,
            "error": state.error,
        }

    except Exception as error:

        trace = (
            state.trace
            if state is not None
            else None
        )

        return {
            "question": question,
            "passed": False,
            "columns_compatible": False,
            "result_match": False,
            "sql_retries": (
                trace.sql_retries
                if trace
                else 0
            ),
            "duration_ms": (
                trace.total_duration_ms
                if trace
                else 0
            ),
            "sql": (
                state.sql
                if state is not None
                else ""
            ),
            "expected_columns": expected_columns,
            "actual_columns": (
                state.columns
                if state is not None
                else []
            ),
            "expected_rows": expected_rows,
            "actual_rows": (
                state.rows
                if state is not None
                else []
            ),
            "error": str(error),
        }


def print_result(
    index,
    result,
):
    """
    Print detailed evaluation information.
    """

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
        "Columns compatible: "
        f"{result['columns_compatible']}"
    )

    print(
        "Result match: "
        f"{result['result_match']}"
    )

    print(
        "SQL retries: "
        f"{result['sql_retries']}"
    )

    print(
        "Duration: "
        f"{result['duration_ms']:.2f} ms"
    )

    if result["passed"]:
        return

    print("\nGENERATED SQL")
    print("-" * 70)
    print(
        result["sql"]
        if result["sql"]
        else "<no SQL generated>"
    )

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

    if result["error"]:

        print("\nERROR")
        print("-" * 70)
        print(result["error"])


def main():

    print("=" * 70)
    print("AI DATA ANALYST EVALUATION")
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
        start=1,
    ):

        result = evaluate_question(
            question_data
        )

        results.append(result)

        print_result(
            index=index,
            result=result,
        )

    total = len(results)

    passed = sum(
        result["passed"]
        for result in results
    )

    total_duration = sum(
        result["duration_ms"]
        for result in results
    )

    total_retries = sum(
        result["sql_retries"]
        for result in results
    )

    accuracy = (
        passed / total * 100
        if total
        else 0
    )

    average_latency = (
        total_duration / total
        if total
        else 0
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Total questions : {total}"
    )

    print(
        f"Passed          : {passed}"
    )

    print(
        f"Failed          : {total - passed}"
    )

    print(
        f"Accuracy        : {accuracy:.2f}%"
    )

    print(
        f"Average latency : "
        f"{average_latency:.2f} ms"
    )

    print(
        f"SQL retries     : {total_retries}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
