from streamlit.testing.v1 import AppTest


def test_running():
    app = AppTest.from_file("src/ordo/__init__.py")
    app.run()
    assert not app.exception
