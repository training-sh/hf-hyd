# If needed:
# %pip install -q "google-adk[gcp]>=2.0.0,<3.0.0"

import os

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner


# ---------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------

PROJECT_ID = os.getenv(
    "GOOGLE_CLOUD_PROJECT",
    "project-id",
)

LOCATION = os.getenv(
    "GOOGLE_CLOUD_LOCATION",
    "global",
)

MODEL_ID = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash-lite",
)


# Tell ADK / Google GenAI to use Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION


print("Project :", PROJECT_ID)
print("Location:", LOCATION)
print("Model   :", MODEL_ID)


# ---------------------------------------------------------
# 2. Normal Python functions
# ---------------------------------------------------------

def add(a: float, b: float) -> float:
    """Add two numbers."""

    print("\n>>> Python add() called")
    print(">>> a =", a)
    print(">>> b =", b)

    result = a + b

    print(">>> result =", result)

    return result


def sub(a: float, b: float) -> float:
    """Subtract b from a."""

    print("\n>>> Python sub() called")
    print(">>> a =", a)
    print(">>> b =", b)

    result = a - b

    print(">>> result =", result)

    return result


# ---------------------------------------------------------
# 3. Create ADK Agent
# ---------------------------------------------------------

root_agent = Agent(
    name="calculator_agent",

    model=Gemini(
        model=MODEL_ID,
    ),

    instruction="""
You are a simple calculator agent.

Rules:
- For addition, use the add tool.
- For subtraction, use the sub tool.
- Always use a tool instead of calculating the answer yourself.
- Return the final result clearly.
""",

    tools=[
        add,
        sub,
    ],
)


# ---------------------------------------------------------
# 4. Create local ADK runner
# ---------------------------------------------------------

runner = InMemoryRunner(
    agent=root_agent,
    app_name="calculator_app",
)


print("\nADK calculator agent ready.")
