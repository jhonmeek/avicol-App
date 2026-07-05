import pytest

from database import Database


def test_migration_v5_tables_stock(tmp_path):
    db = Database(db_name=tmp_path / "v5.db")
    assert db.get_schema_version() == db.SCHEMA_VERSION
    tables = {
        row[0]
        for row in db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    db.close()
    assert {"stocks", "mouvements_stock"} <= tables


def test_ajouter_article_stock_stock_initial_zero(tmp_path):
    db = Database(db_name=tmp_path / "stock1.db")
    stock_id = db.ajouter_article_stock(
        "Aliment démarrage", "aliment", "kg", seuil_alerte=50
    )
    quantite = db.get_stock_quantite(stock_id)
    articles = db.get_articles_stock()
    db.close()
    assert quantite == 0
    assert articles[0][1] == "Aliment démarrage"
    assert articles[0][2] == "aliment"
    assert articles[0][3] == "kg"
    assert articles[0][4] == 50


def test_ajouter_article_stock_refuse_categorie_invalide(tmp_path):
    db = Database(db_name=tmp_path / "stock2.db")
    with pytest.raises(ValueError):
        db.ajouter_article_stock("Article X", "inconnu", "kg")
    db.close()
