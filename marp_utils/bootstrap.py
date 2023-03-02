import inquirer
from inquirer.themes import GreenPassion

from ._bootstrapper import Bootstrapper


def boostrap_presentation():
    print("\t" + "*" * 32)
    print("\t Marp Presentation Bootstrapper")
    print("\t" + "*" * 32)
    print("")

    questions = [
        inquirer.Path("output_path", message="Path to file (has to end in '.md')"),
        inquirer.Text("title", message="What is the title of your presentation?"),
        inquirer.Text(
            "subtitle",
            message="What is the sub-title of your presentation?",
            default=None,
        ),
        inquirer.Text("event", message="What is the event of your presentation?"),
        inquirer.Text(
            "date",
            message="What is the date of your presentation?",
        ),
        inquirer.Checkbox(
            "options",
            message="Pick the optional components you would like",
            choices=["pagination", "header", "footer", "img-center"],
        ),
        inquirer.Confirm("sections", message="Do you want to add sections?"),
    ]

    answers = inquirer.prompt(questions, theme=GreenPassion())

    def get_sections(i=0, prev_answers=None):
        if prev_answers is None:
            prev_answers = {}

        questions = [
            inquirer.Text(
                "section",
                message=f"What is the title of section #{i+1}? (leave empty to finish process)",
            )
        ]

        answers = inquirer.prompt(questions, theme=GreenPassion())

        if answers["section"]:
            prev_answers[f"section_{i}"] = answers["section"]
            out_answers = get_sections(i=i + 1, prev_answers=prev_answers)
        else:
            out_answers = prev_answers

        return out_answers

    if answers["sections"]:
        answers["sections"] = list(get_sections().values())
    else:
        answers["sections"] = []

    file_path = answers.pop("output_path")

    bootstrapper = Bootstrapper(**answers)
    bootstrapper.bootstrap(file_path=file_path)
