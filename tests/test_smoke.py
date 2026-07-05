def test_harness_imports_database():
    import database  # doit être importable via pythonpath = .

    assert hasattr(database, "Database")
