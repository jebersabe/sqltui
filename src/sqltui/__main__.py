from rich import print
from rich.panel import Panel
from sqltui.main import SqlTUI


def main():
    app = SqlTUI()
    app.run()


if __name__ == "__main__":
    main()
    print(
        Panel.fit(
            "[b magenta]Hope you liked the demo![/]\n\n"
            "Please consider sponsoring me if you get value from my work.\n\n"
            "Even the price of a ☕ can brighten my day!\n\n"
            "https://github.com/sponsors/willmcgugan\n\n"
            "- Will McGugan",
            border_style="red",
            title="Consider sponsoring",
        )
    )
