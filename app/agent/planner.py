"""
Planning component for AI Data Analyst.

Determines which registered tools are required
to answer a user's analytics question.
"""

import json
import re

from app.llm.client import generate_response
from app.tools.registry import list_tools


def build_planner_prompt(question: str) -> str:
    """
    Build the prompt used by the planner LLM.
    """
    available_tools = list_tools()

    return f"""
You are the planning component of an AI data analyst.

Your job is to determine which tools are required
to answer the user's question.

USER QUESTION
-------------
{question}

AVAILABLE TOOLS
---------------
{json.dumps(available_tools, indent=2)}

TOOL PURPOSES
-------------
sql_query:
Retrieve data from the PostgreSQL database.

create_dataframe:
Convert SQL results into a Pandas DataFrame.

calculate_percentage:
Calculate percentage contribution of values.

calculate_summary:
Calculate numerical summary statistics.

create_bar_chart:
Create a bar chart from tabular data.

PLANNING RULES
--------------
1. Select only tools from the available tools list.
2. Select the minimum tools necessary.
3. Always use sql_query when database data is required.
4. Use create_dataframe only when Python/Pandas processing
   is actually required.
5. Use calculate_percentage only when percentage contribution
   must be calculated.
6. Use calculate_summary only when statistical summary
   is explicitly required.
7. Use create_bar_chart only when a chart, graph,
   visualization, or similar visual output is requested.
8. Do not select tools that are not necessary.
9. Return ONLY a JSON array of tool names.
10. Do not use Markdown code fences.
11. Do not include explanations.

EXAMPLES
--------
Question: What is the total number of orders?
Answer: ["sql_query"]

Question: What percentage of revenue came from each category?
Answer: ["sql_query", "create_dataframe", "calculate_percentage"]

Question: Show revenue by category as a chart.
Answer: ["sql_query", "create_dataframe", "create_bar_chart"]

Question: Give me the average and maximum revenue by category.
Answer: ["sql_query", "create_dataframe", "calculate_summary"]

TOOL PLAN:
""".strip()


def clean_planner_response(response: str) -> str:
    """
    Remove common Markdown formatting around JSON.
    """
    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    return response.strip()


def plan_tools(question: str) -> list[str]:
    """
    Ask the LLM to select the tools required
    for the user's question.
    """
    prompt = build_planner_prompt(question)

    response = generate_response(prompt)

    cleaned_response = clean_planner_response(response)

    try:
        tools = json.loads(cleaned_response)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Planner returned invalid JSON: {response}"
        ) from error

    if not isinstance(tools, list):
        raise ValueError(
            "Planner output must be a JSON array."
        )

    available_tools = set(list_tools())

    for tool in tools:
        if tool not in available_tools:
            raise ValueError(
                f"Planner selected unknown tool: {tool}"
            )

    return tools