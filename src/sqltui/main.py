import multiprocessing
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, DataTable, Button, Static
from textual.containers import Horizontal, Vertical, VerticalGroup, HorizontalGroup
from sqltui.backend import odps_from_env
import logging
from textual.logging import TextualHandler

logger = logging.getLogger(__name__)
logger.addHandler(TextualHandler())
logger.setLevel(logging.INFO)

o = odps_from_env()


class ButtomButtons(HorizontalGroup):
    def compose(self):
        with Horizontal():
            yield Button("Run", variant="default", id="run")
            yield Button("Clear", variant="default", id="clear")
            yield Button("Exit", variant="default", id="exit")


class LeftPanel(VerticalGroup):
    def compose(self):
        with Vertical():
            yield Static("Query", id="query_header")
            yield TextArea.code_editor("", language="sql", id="input_query")
            yield ButtomButtons()


class RightPanel(VerticalGroup):
    def compose(self):
        with Vertical():
            yield Static("Result", id="result_header")
            yield DataTable()


class SqlTUI(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+enter", "run_query", "Run Query"),
    ]
    CSS_PATH = "sqltui.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal():
            yield LeftPanel()
            yield RightPanel()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "catppuccin-mocha" if self.theme == "textual-light" else "textual-light"
        )

    def action_run_query(self) -> None:
        run_button = self.query_one("#run")
        run_button.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            table = self.query_one(DataTable)
            table.clear(columns=True)
            query = self.query_one(TextArea)
            query_text = query.text

            if query_text:
                table.loading = True
                self.load_data(query_text, table)
                table.loading = False

        if event.button.id == "clear":
            text_area = self.query_one(TextArea)
            text_area.clear()

        if event.button.id == "exit":
            self.exit()

    def load_data(self, query: str, data_table: DataTable) -> None:
        n_process = multiprocessing.cpu_count()
        instance = None
        try:
            instance = o.execute_sql(query)
            with instance.open_reader(tunnel=True) as reader:
                df = reader.to_pandas(n_process=n_process)
            df_dict = df.to_dict(orient="split")
            rows = df_dict["data"]
            columns = list(df.columns)
            data_table.add_columns(*columns)
            data_table.add_rows(rows)
        except Exception as e:
            self.app.notify(f"Encountered error: {e}", title="ERROR", severity="error")
        finally:
            if instance and not instance.is_terminated():
                o.stop_instance(instance.id)


if __name__ == "__main__":
    app = SqlTUI()
    app.run()
