from app import app

def test_add():
    with app.test_client() as c:
        rv = c.post("/", data={"a":"2","b":"3","op":"add"})
        assert b"Result: 5.0" in rv.data
