from google.genai import types

from course_config import MODEL_ID, make_client


# ---------------------------------------------------------
# 1. Normal Python functions
# ---------------------------------------------------------

def add(a, b):
    return a + b


def sub(a, b):
    return a - b


# ---------------------------------------------------------
# 2. Register Python functions locally
# ---------------------------------------------------------

TOOL_REGISTRY = {
    "add": add,
    "sub": sub,
}


# ---------------------------------------------------------
# 3. Describe the functions to Gemini
# ---------------------------------------------------------

add_function = types.FunctionDeclaration(
    name="add",
    description="Add two numbers.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["a", "b"],
    },
)


sub_function = types.FunctionDeclaration(
    name="sub",
    description="Subtract b from a.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
        "required": ["a", "b"],
    },
)


tools = types.Tool(
    function_declarations=[
        add_function,
        sub_function,
    ]
)


# ---------------------------------------------------------
# 4. Gemini configuration
# ---------------------------------------------------------

config = types.GenerateContentConfig(
    tools=[tools],

    # We want to execute Python ourselves so students
    # can see what is happening.
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    ),
)


# ---------------------------------------------------------
# 5. Ask Gemini
# ---------------------------------------------------------

question = "What is 25 plus 17?"

messages = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=question)
        ],
    )
]


with make_client() as client:

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=messages,
        config=config,
    )

    content = response.candidates[0].content

    # -----------------------------------------------------
    # 6. Check whether Gemini requested a function
    # -----------------------------------------------------

    function_call = next(
        (
            part.function_call
            for part in content.parts
            if part.function_call is not None
        ),
        None,
    )

    if function_call:

        print("Gemini selected function:")
        print(function_call.name)

        print("\nArguments:")
        print(function_call.args)

        # -------------------------------------------------
        # 7. Execute our Python function
        # -------------------------------------------------

        python_function = TOOL_REGISTRY[function_call.name]

        result = python_function(**function_call.args)

        print("\nPython result:")
        print(result)
