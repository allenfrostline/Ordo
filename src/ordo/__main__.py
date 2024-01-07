if __name__ == "__main__":
    import pathlib
    import sys

    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(pathlib.Path(__file__).parent.resolve() / "app.py"),
        "--server.runOnSave",
        "true",
        "--theme.base",
        "light",
    ]
    sys.exit(stcli.main())
