import monkey_object as mobject

def test_string_hash_key():
    hello1 = mobject.String(value="Hello World")
    hello2 = mobject.String(value="Hello World")
    diff1 = mobject.String(value="different string")
    diff2 = mobject.String(value="different string")

    assert hello1.hash_key == hello2.hash_key, "strings with same content have different hash keys"
    assert hello1.hash_key != diff1.hash_key, "strings with different content have same hash keys"
    assert diff1.hash_key == diff2.hash_key, "strings with same content have different hash keys"

def test_int_hash_key():
    a1 = mobject.Integer(value=1)
    a2 = mobject.Integer(value=1)
    diff = mobject.Integer(value=30)

    assert a1.hash_key == a2.hash_key, "int with same content have different hash keys"
    assert a1.hash_key != diff.hash_key, "int with different content have same hash keys"

def test_bool_hash_key():
    t1 = mobject.Boolean(value=True)
    t2 = mobject.Boolean(value=True)
    f1 = mobject.Boolean(value=False)

    assert t1.hash_key == t2.hash_key, "bool with same content have different hash keys"
    assert t1.hash_key != f1.hash_key, "bool with different content have same hash keys"