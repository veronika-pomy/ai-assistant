from rich.console import Console
from dotenv import load_dotenv
from openai import OpenAI
import json
load_dotenv(override=True)

def show(text):
    try:
        Console().print(text)
    except Exception:
        print(text)

openai = OpenAI()

# Model configuration
MODEL = "gpt-5.5"

# Set up lists for agent to use
checklist = []
completed = []

# Print the report of the checklist completion status
def get_checklist_report() -> str:
    result = ''
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result

# Create a checklist and return the report
def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_checklist_report()

# Mark completed checklist items and return the report
def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return 'No checklist item found at that index.'
    show(completion_notes)
    return get_checklist_report()

# Define tool JSON schema for agent to use
create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                'type': 'array',
                'items': {'type': 'string'},
                'title': 'Descriptions of checklist items'
                }
            },
        "required": ["descriptions"],
        "additionalProperties": False
    }
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        'properties': {
            'index': {
                'description': 'The 1-based index of the checklist item to mark as complete',
                'title': 'Index',
                'type': 'integer'
                },
            'completion_notes': {
                'description': 'Notes about how you completed the checklist item in rich console markup',
                'title': 'Completion Notes',
                'type': 'string'
                }
            },
        'required': ['index', 'completion_notes'],
        'type': 'object',
        'additionalProperties': False
    }
}

tools = [{"type": "function", "function": create_checklist_json},
        {"type": "function", "function": mark_complete_json}]

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**args) if tool else {}
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results

def loop(messages):
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    show(response.choices[0].message.content)

# System message for the agent
system_message = """
You are a helpful assistant with a knack for solving creative and logical problems.
You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
Now create a plan, set the checklist, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""

# Get user input
def get_user_task():
    """Get task input from user"""
    console = Console()

    # Agent welcome message
    top_section = r"""[plum2]
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣴⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ▄▄▄   ▄▄▄          ▄▄▄▄▄ ▄           ▄▄▄    ▄▄▄       ▄▄ ▄▄
⠀⠀⠀⣠⣖⠶⣤⣴⠚⠛⠍⡠⢌⠉⠙⠳⣦⡤⠖⣲⣄⠀⠀⠀    ███   ███ ▀▀        ███  ▀           ████▄  ███       ██ ██
⠀⢀⣤⡿⢉⣹⣌⠈⠀⢀⠌⠀⠀⠡⡀⠀⠁⣠⣟⡉⢿⣤⡀⠀    █████████ ██        ███   ███▄███▄   ███▀██▄███ ▄█▀█▄ ██ ██ ▄█▀█▄
⠀⠸⣇⡀⠘⢩⠊⢀⡀⢸⠀⠀⠀⠀⡧⢀⡀⠑⢜⠃⢀⣨⠇⠀    ███▀▀▀███ ██        ███   ██ ██ ██   ███  ▀████ ██▄█▀ ██ ██ ██▄█▀
⠀⠀⢠⠏⠑⠁⠀⣿⡟⡘⠀⠀⠀⠀⢣⢻⣿⠀⠈⠪⡹⡇⠀⠀    ███   ███ ██▄ ▄▄   ▄███▄  ██ ██ ██   ███    ███ ▀█▄▄▄ ██ ██ ▀█▄▄▄ ██
⠀⢠⡿⠁⠀⠀⠀⢀⠜⠀⠀⠀⠀⠀⠀⠡⡀⠀⠀⠀⠈⢹⡄⠀                 ▄█▀
⠀⣾⣇⠀⠀⣀⠔⠁⠀⠀⢠⣌⣩⡆⠀⠀⠈⠢⣀⠀⠀⢸⢷⠀
⢠⡇⢳⡉⠁⠀⠀⠀⠀⠀⣀⣹⣏⣀⠀⠀⠀⠀⠀⠈⢁⡾⢸⡆
⢸⢡⠀⠑⢤⡀⠀⠀⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⢀⡠⠚⠀⡌⡇
⢸⡄⢣⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⡘⢀⡇
⠈⣯⢦⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣶⢾⣔⣽⠁
⠀⠈⠿⣮⠀⢓⠢⣂⡀⢩⡀⠐⠂⢈⡼⢀⣀⡴⡺⠁⣰⡿⠁⠀
⠀⠀⠀⠈⠓⠛⠉⠹⠿⠿⠛⠛⠛⠛⠿⠷⠏⠉⠛⠚⠁⠀⠀⠀[/plum2]
    """

    bottom_section = r"""[plum2]
▄▄▄   ▄▄▄                       ▄▄ ▄▄         ▄▄   ▄▄                                                             ▄▄
███   ███                      ██  ██        ██   ██                            ▀▀         ██               ██    ██
▀███▄███▀ ▄███▄ ██ ██ ████▄   ▀██▀ ██ ██ ██ ▀██▀ ▀██▀ ██ ██    ▀▀█▄ ▄█▀▀▀ ▄█▀▀▀ ██  ▄█▀▀▀ ▀██▀▀ ▀▀█▄ ████▄ ▀██▀▀  ██
  ▀███▀   ██ ██ ██ ██ ██ ▀▀    ██  ██ ██ ██  ██   ██  ██▄██   ▄█▀██ ▀███▄ ▀███▄ ██  ▀███▄  ██  ▄█▀██ ██ ██  ██    ▀▀
   ███    ▀███▀ ▀██▀█ ██       ██  ██ ▀██▀█  ██   ██   ▀██▀   ▀█▄██ ▄▄▄█▀ ▄▄▄█▀ ██▄ ▄▄▄█▀  ██  ▀█▄██ ██ ██  ██    ██
                                                        ██
                                                      ▀▀▀[/plum2]
    """

    console.print("\n")
    console.print(top_section)
    console.print(bottom_section)
    console.print("[plum2][dim]Let's tackle whatever you need today, step by step.[/dim][/plum2]\n")

    console.print("[bold yellow]→ What can I help you with?[/bold yellow]")
    user_input = input("\n  >> ")
    return user_input

def main():
    while True:
        user_input = get_user_task()

        # Check if input is empty or only whitespace
        if not user_input.strip():
            show("[yellow]Looks like that was empty - try again![/yellow]")
            continue

        # Build messages with user's input
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]

        # Run the agent loop
        loop(messages)

        # Ask if user wants to continue
        continue_prompt = input("\n\nWant to work on something else? (yes/no): ")
        if continue_prompt.lower() not in ['yes', 'y']:
            show("[green]Thanks! Have a great day![/green]")
            break

# Run main() when script is executed directly, not when imported as a module
if __name__ == "__main__":
    main()
    