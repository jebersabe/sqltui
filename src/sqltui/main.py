from textual import on
import pandas as pd
import multiprocessing
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, DataTable, Button, Select
from textual.containers import Horizontal, Vertical, VerticalScroll, HorizontalGroup
from sqltui.backend import odps_from_env, load_config
import logging
from textual.logging import TextualHandler


logger = logging.getLogger(__name__)
logger.addHandler(TextualHandler())
logger.setLevel(logging.INFO)


class ButtomButtons(HorizontalGroup):
    def compose(self):
        yield Button("Run", variant="default", id="run")
        yield Button("Check Partitions", variant="default", id="check_pt")
        yield Button("Clear", variant="default", id="clear")
        yield Button("Exit", variant="default", id="exit")


class LeftPanel(VerticalScroll):
    def compose(self):
        yield TextArea.code_editor(
            "", language="sql", theme="vscode_dark", id="input_query"
        )
        yield ButtomButtons()


class SqlTUI(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        ("ctrl+enter", "run_query", "Run Query"),
        ("ctrl+t", "check_pt", "Check Partitions"),
        ("ctrl+l", "clear_query", "Clear"),
    ]
    CSS_PATH = "sqltui.tcss"
    TITLE = "SQLTUI"

    def __init__(self):
        super().__init__()
        self.o = None
        self.project_options = [("", "")]
        self.projects = []
        self.selected_project = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Vertical():
            yield Header()
            yield Select(self.project_options, id="select_project")
            with Horizontal(id="main_area"):
                yield LeftPanel(id="left_panel")
                yield DataTable(id="right_panel")
            yield Footer()

    def action_run_query(self) -> None:
        run_button = self.query_one("#run")
        run_button.press()

    def action_clear_query(self) -> None:
        clear_button = self.query_one("#clear")
        clear_button.press()

    def action_check_pt(self) -> None:
        check_pt_button = self.query_one("#check_pt")
        check_pt_button.press()

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        left_panel_wid = self.get_widget_by_id("left_panel")
        left_panel_wid.border_title = "QUERY"

        right_panel_wid = self.get_widget_by_id("right_panel")
        right_panel_wid.border_title = "RESULT"

        text_area_wid = self.get_widget_by_id("input_query")
        text_area_wid.focus()

        select_widget = self.get_widget_by_id("select_project")
        select_widget.border_title = "PROJECT"

        try:
            self.projects = load_config("config.yaml")["projects"]
        except FileNotFoundError:
            logger.error("config.yaml not found. Please create the config file.")
            raise FileNotFoundError(
                "config.yaml not found. Please create the config file."
            )
        else:
            self.project_options = [
                (proj["name"], proj["name"]) for proj in self.projects
            ]
            select_widget.set_options(self.project_options)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            table = self.query_one(DataTable)
            table.clear(columns=True)
            query = self.query_one(TextArea)
            query_text = query.text.strip()

            if not self.selected_project:
                self.app.notify(
                    "No project selected. Please select a project from the dropdown.",
                    title="WARNING",
                    severity="warning",
                )
                return

            if query_text:
                table.loading = True
                self.load_data(query_text, table)
                table.loading = False

        if event.button.id == "clear":
            text_area = self.query_one(TextArea)
            table = self.query_one(DataTable)
            text_area.clear()

        if event.button.id == "exit":
            self.exit()

        if event.button.id == "check_pt":
            self.check_partition()

    def load_data(self, query: str, data_table: DataTable) -> pd.DataFrame:
        n_process = multiprocessing.cpu_count()
        try:
            instance = self.o.execute_sql(query)
            with instance.open_reader(tunnel=True) as reader:
                df = reader.to_pandas(n_process=n_process)
            df_dict = df.to_dict(orient="split")
            rows = df_dict["data"]
            columns = list(df.columns)
            data_table.add_columns(*columns)
            data_table.add_rows(rows)
        except Exception as e:
            self.app.notify(
                f"Encountered error: {str(e)[:500]}", title="ERROR", severity="error"
            )

    def check_partition(self) -> None:
        table_name = self.query_one(TextArea).text.strip()
        if not table_name:
            return
        data_table = self.query_one(DataTable)
        data_table.clear(columns=True)

        # catch error when checking for table existence
        try:
            table_exists = self.o.exist_table(table_name)
        except Exception as e:
            self.app.notify(
                f"Encountered error: {str(e)[:300]}", title="ERROR", severity="error"
            )
            return

        if not table_exists:
            self.app.notify("Table does not exist", title="WARNING", severity="warning")
            return
        # catch error when checking table partitions
        try:
            table_obj = self.o.get_table(table_name)
            pt_list = [(pt.name,) for pt in table_obj.partitions]
            data_table.add_column("Partitions")
            data_table.add_rows(pt_list)
            data_table.sort(reverse=True)
        except Exception as e:
            self.app.notify(
                f"Encountered error: {str(e)[:300]}", title="ERROR", severity="error"
            )
            return

    @on(Select.Changed, "#select_project")
    def select_changed(self, event: Select.Changed) -> None:
        self.selected_project = str(event.value)

        match_projects = [
            project
            for project in self.projects
            if project["name"] == self.selected_project
        ]

        if not match_projects:
            self.app.notify(
                "Selected project not found in config.yaml",
                title="ERROR",
                severity="error",
            )
            raise Exception("Selected project not found in config.yaml")

        project_dict = match_projects[0]

        self.o = odps_from_env(
            id_key=project_dict["access_key"],
            secret_key=project_dict["secret_key"],
            project=project_dict["name"],
        )


if __name__ == "__main__":
    app = SqlTUI()
    app.run()
