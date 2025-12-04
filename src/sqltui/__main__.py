from sqltui.main import SqlTUI
import sys


def main():
    if len(sys.argv) > 1:
        print("SqlTUI does not accept command line arguments.")
        sys.exit(1)

    app = SqlTUI()
    app.run()


if __name__ == "__main__":
    main()
