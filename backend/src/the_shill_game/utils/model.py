from pydantic import BaseModel
from the_shill_game import openai_client


def invoke_chat_response(
    input: str, instruction: str = "", model: str = "gpt-4o"
) -> str:
    """Invoke a model and return the response"""
    messages = []
    if instruction:
        messages.append({"role": "system", "content": instruction})
    messages.append({"role": "user", "content": input})
    return (
        openai_client.chat.completions.create(model=model, messages=messages)
        .choices[0]
        .message.content
    )


def invoke_structured_response(
    input: str,
    response_format: BaseModel,
    instruction: str = "",
    model: str = "gpt-4o",
) -> BaseModel:
    """Invoke a model and return a structured response"""
    messages = []
    if instruction:
        messages.append({"role": "system", "content": instruction})
    messages.append({"role": "user", "content": input})

    return (
        openai_client.beta.chat.completions.parse(
            model=model, messages=messages, response_format=response_format
        )
        .choices[0]
        .message.parsed
    )


if __name__ == "__main__":
    print(invoke_chat_response("Hello, world!"))

    class Step(BaseModel):
        explanation: str
        output: str

    class MathReasoning(BaseModel):
        steps: list[Step]
        final_answer: str

    res = invoke_structured_response(
        instruction="You are a helpful math tutor. Guide the user through the solution step by step.",
        input="how can I solve 8x + 7 = -23",
        response_format=MathReasoning,
    )
    print(
        "\n".join(
            f"Explanation: {step.explanation}\nOutput: {step.output}\n-------"
            for step in res.steps
        )
    )
