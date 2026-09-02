import os
import requests
import json
import asyncio
from rich.console import Console
from rich.live import Live
from rich.text import Text
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, SQLiteSession, trace, function_tool
load_dotenv(override=True)
MODEL_NAME = os.getenv("MODEL_NAME")

# General util
def show(text):
    try:
        Console().print(text)
    except Exception:
        print(text)

# Helper code
checklist = []
completed = []

def _checklist_report() -> str:
    result = ''
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"Checklist #{index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"Checklist #{index + 1}: {item}\n"
    show(result)
    return result

# Tools
@function_tool
def create_checklist(descriptions: list[str]) -> str:
    """
    Create a checklist and return the report

    Args:
        descriptions: list of tasks
    """
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return _checklist_report()

@function_tool
def mark_complete(index: int, completion_notes: str) -> str:
    """
    Mark completed checklist items and return the report

    Args:
        index: of the task to make as complete
        completion notes: notes from the agent about status of the task
    """
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return 'No checklist item found at that index.'
    show(completion_notes)
    return _checklist_report()

tools = [ create_checklist, mark_complete ]

# Welcome banner
def show_welcome():
    console = Console()

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
    console.print('[bold bright_blue]Tip: type "exit" or "quit" any time to close the agent.[/bold bright_blue]\n')

# Prompt for user task
def prompt_user(first=False):
    if first:
        Console().print("[bold yellow]→ What can I help you with?[/bold yellow]")
    return input("\n  >> ")

async def main():
    show_welcome()
    session = SQLiteSession("nelle", ":memory:")
    first = True
    while True:
        user_input = prompt_user(first=first)
        first = False

        # Check if input is empty or whitespace
        if not user_input.strip():
            show("[yellow]Looks like that was empty - try again![/yellow]")
            continue

        # Exit on quit commands
        if user_input.strip().lower() in ('exit', 'quit'):
            show("[green]Thanks! Have a great day![/green]")
            break

        system_message = """
        You are a helpful assistant with a knack for solving creative and logical problems.
        You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
        Now create a plan, set the checklist, carry out the steps, and reply with the solution.
        If anything isn't provided in the question, then include a step to come up with a reasonable estimate.
        Provide your solution in Rich console markup without code blocks.
        Use bold and color only for emphasis on specific words or short phrases — do not style entire sentences or paragraphs. Body text should remain plain.
        Do not ask the user questions or clarification; respond only with the answer after using your tools.
        """

        agent = Agent(name="Nelle", instructions=system_message, tools=tools, model=MODEL_NAME)

        task = user_input

        # Run the agent and stream response
        with trace("Nelle Assistant"):
            result = Runner.run_streamed(agent, task, session=session)
            buffer = ''
            with Live(Text.from_markup(''), refresh_per_second=20) as live:
                async for event in result.stream_events():
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        buffer += event.data.delta
                        live.update(Text.from_markup(buffer))

if __name__ == "__main__":
    asyncio.run(main())
