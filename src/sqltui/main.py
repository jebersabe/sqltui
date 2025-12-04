from textual import on
import multiprocessing
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, TextArea, DataTable, Button, Select
from textual.containers import Horizontal, Vertical, VerticalScroll, HorizontalGroup
from sqltui.backend import odps_from_env, load_config
from sqltui.crud import (
    initialize_database,
    insert_query,
    fetch_queries,
    delete_database,
)
import logging
from textual.logging import TextualHandler
from pathlib import Path


logger = logging.getLogger(__name__)
logger.addHandler(TextualHandler())
logger.setLevel(logging.INFO)


class ButtomButtons(HorizontalGroup):
    def compose(self):
        yield Button("Run", variant="default", id="run")
        yield Button("Partitions", variant="default", id="check_pt")
        yield Button("Schema", variant="default", id="schema_button")
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
        self.past_queries = []
        self.query_options = [("", "")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Vertical():
            yield Static("SQLTUI", id="header")
            with Horizontal(id="select_horizontal_container"):
                yield Select(self.project_options, id="select_query")
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

        select_widget_project = self.get_widget_by_id("select_project")
        select_widget_project.focus()
        select_widget_project.border_title = "PROJECT"

        select_widget_query = self.get_widget_by_id("select_query")
        select_widget_query.border_title = "HISTORY"

        # Initialize database if it doesn't exist
        db_path = Path("queries.db")
        if not db_path.exists():
            initialize_database()

        self.past_queries = dict.fromkeys(fetch_queries())
        self.query_options = [(q[0][:100], q[0]) for q in self.past_queries]
        select_widget_query.set_options(self.query_options)

        try:
            self.projects = load_config("config.yaml")["projects"]
        except FileNotFoundError:
            logger.error("config.yaml not found. Please create the config file.")
            self.app.notify(
                "config.yaml not found. Please create the config file.",
                title="ERROR",
                severity="error",
            )
        else:
            self.project_options = [
                (proj["name"], proj["name"]) for proj in self.projects
            ]
            select_widget_project.set_options(self.project_options)

    @on(Button.Pressed, "#schema_button")
    async def show_schema(self):
        data_table = self.query_one(DataTable)
        data_table.clear(columns=True)
        data_table.loading = True
        self.get_schema(data_table)

    @on(Button.Pressed, "#run")
    async def run_query(self):
        table = self.query_one(DataTable)
        table.clear(columns=True)
        query = self.query_one("#input_query")
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

    @on(Button.Pressed, "#clear")
    def clear_text_editor(self):
        text_area = self.query_one("#input_query")
        text_area.clear()

    @on(Button.Pressed, "#exit")
    def exit_app(self):
        self.exit()

    @on(Button.Pressed, "#check_pt")
    async def check_table_pt(self):
        if not self.selected_project:
            self.app.notify(
                "No project selected. Please select a project from the dropdown.",
                title="WARNING",
                severity="warning",
            )
            return

        data_table = self.query_one(DataTable)
        data_table.loading = True
        self.check_partition(data_table)

    @work(exclusive=True, thread=True)
    async def load_data(self, query: str, data_table: DataTable) -> None:
        if "limit" not in query.lower():
            pass
        insert_query(query)
        self.refresh_history()
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
        finally:
            data_table.loading = False

    @work(exclusive=True, thread=True)
    async def check_partition(self, data_table) -> None:
        table_name = self.query_one("#input_query").text.strip()
        insert_query(table_name)
        self.refresh_history()
        if not table_name:
            data_table.loading = False
            return
        data_table.clear(columns=True)

        # catch error when checking for table existence
        try:
            table_exists = self.o.exist_table(table_name)
        except Exception as e:
            self.app.notify(
                f"Encountered error: {str(e)[:300]}", title="ERROR", severity="error"
            )
            return
        finally:
            data_table.loading = False

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
        finally:
            data_table.loading = False

    @work(exclusive=True, thread=True)
    async def get_schema(self, data_table: DataTable):
        if not self.selected_project:
            self.app.notify("No project selected", title="WARNING", severity="warning")
            data_table.loading = False
            return

        table_name = self.query_one("#input_query").text.strip()
        insert_query(table_name)
        self.refresh_history()
        if not table_name:
            self.app.notify(
                "Please provide a table name", title="WARNING", severity="warning"
            )
            data_table.loading = False
            return

        try:
            table_obj = self.o.get_table(table_name)
            schema_obj = table_obj.schema
        except Exception as e:
            self.app.notify(
                f"Encountered error: {str(e)[:300]}", title="ERROR", severity="error"
            )
            return
        else:
            columns = ["column", "type", "comment"]
            rows = []
            for schema in schema_obj:
                rows.append((schema.name, schema.type, schema.comment))

            data_table.add_columns(*columns)
            data_table.add_rows(rows)
        finally:
            data_table.loading = False

    @on(Select.Changed, "#select_query")
    async def select_changed_query(self, event: Select.Changed) -> None:
        if event.value == Select.BLANK:
            return
        selected_query = str(event.value)
        text_area = self.query_one("#input_query")
        text_area.text = selected_query

    @on(Select.Changed, "#select_project")
    async def select_changed_project(self, event: Select.Changed) -> None:
        self.selected_project = str(event.value)
        if event.value == Select.BLANK:
            self.app.notify("No project selected", title="INFO", severity="info")
            return

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
        self.load_odps(project_dict)

    @work(exclusive=True, thread=True)
    async def load_odps(self, project_dict):
        self.o = odps_from_env(
            id_key=project_dict["access_key"],
            secret_key=project_dict["secret_key"],
            project=project_dict["name"],
        )

    def refresh_history(self):
        select_widget_query = self.get_widget_by_id("select_query")
        self.past_queries = dict.fromkeys(fetch_queries())
        self.query_options = [(q[0][:100], q[0]) for q in self.past_queries]
        select_widget_query.set_options(self.query_options)


if __name__ == "__main__":
    app = SqlTUI()
    app.run()
