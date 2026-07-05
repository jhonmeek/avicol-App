# database.py
import sqlite3
from datetime import datetime

from app_paths import database_path

class Database:
    def __init__(self, db_name=None):
        self.db_name = str(db_name or database_path())
        self.conn = sqlite3.connect(self.db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.create_tables()

    SCHEMA_VERSION = 6

    def create_tables(self):
        """Applique les migrations en attente (idempotent)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS schema_version ("
            "version INTEGER NOT NULL, applied_at TEXT NOT NULL)"
        )
        current = self.get_schema_version()
        for version in range(current + 1, self.SCHEMA_VERSION + 1):
            self._apply_migration(version)
            cursor.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (version, datetime.now().isoformat(timespec="seconds")),
            )
        self.conn.commit()

    def get_schema_version(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='schema_version'"
        )
        if cursor.fetchone() is None:
            return 0
        row = cursor.execute("SELECT MAX(version) FROM schema_version").fetchone()
        return row[0] if row and row[0] is not None else 0

    def _apply_migration(self, version):
        if version == 1:
            self._migration_1_baseline()
        elif version == 2:
            self._migration_2_zootechnie_chair()
        elif version == 3:
            self._migration_3_poids_vente()
        elif version == 4:
            self._migration_4_ponte_mvp()
        elif version == 5:
            self._migration_5_stocks()
        elif version == 6:
            self._migration_6_sanitaire()

    def _migration_1_baseline(self):
        cursor = self.conn.cursor()

        # Table pour les bandes de poulets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_bande TEXT NOT NULL,
                date_debut DATE NOT NULL,
                nombre_initial INTEGER NOT NULL,
                prix_achat_poussin REAL,
                statut TEXT DEFAULT 'en_cours'
            )
        ''')

        # Table pour les mortalités
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mortalites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER,
                date DATE NOT NULL,
                nombre_morts INTEGER NOT NULL,
                cause TEXT,
                description TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')

        # Table pour les dépenses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS depenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER,
                date DATE NOT NULL,
                type_depense TEXT NOT NULL,
                description TEXT,
                montant REAL NOT NULL,
                fournisseur TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')

        # Table pour les ventes/recettes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER,
                date DATE NOT NULL,
                nombre_poulets INTEGER NOT NULL,
                prix_unitaire REAL NOT NULL,
                montant_total REAL NOT NULL,
                client TEXT,
                paiement TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')

        self._ensure_column("mortalites", "description", "TEXT")
        self._ensure_column("depenses", "fournisseur", "TEXT")
        self._ensure_column("ventes", "client", "TEXT")
        self._ensure_column("ventes", "paiement", "TEXT")
        self._create_indexes()

    def _migration_2_zootechnie_chair(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consommations_aliment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                quantite_kg REAL NOT NULL CHECK (quantite_kg > 0),
                type_aliment TEXT,
                observation TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                poids_moyen_g REAL NOT NULL CHECK (poids_moyen_g > 0),
                effectif_pese INTEGER NOT NULL CHECK (effectif_pese > 0),
                observation TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        self._create_zootechnie_indexes()

    def _migration_3_poids_vente(self):
        # Poids total vendu (kg), pour un IC de fin de cycle correct meme
        # apres que tous les sujets d'un lot ont ete vendus.
        self._ensure_column("ventes", "poids_total", "REAL")

    def _migration_4_ponte_mvp(self):
        # Colonne d'activite (chair/ponte) sur les lots existants.
        self._ensure_column("bandes", "activite", "TEXT DEFAULT 'chair'")

        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pontes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                nombre_oeufs INTEGER NOT NULL CHECK (nombre_oeufs > 0),
                observation TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mouvements_oeufs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                type_mouvement TEXT NOT NULL
                    CHECK (type_mouvement IN ('entree_production', 'vente')),
                quantite INTEGER NOT NULL CHECK (quantite > 0),
                prix_unitaire REAL,
                montant REAL,
                client TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        self._create_ponte_indexes()

    def _create_ponte_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pontes_bande_date "
            "ON pontes (bande_id, date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_mouvements_oeufs_bande_date "
            "ON mouvements_oeufs (bande_id, date)"
        )

    def _migration_5_stocks(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_article TEXT NOT NULL,
                categorie TEXT NOT NULL
                    CHECK (categorie IN ('aliment', 'medicament', 'litiere')),
                unite TEXT NOT NULL,
                seuil_alerte REAL NOT NULL DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mouvements_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER NOT NULL,
                date DATE NOT NULL,
                type_mouvement TEXT NOT NULL
                    CHECK (type_mouvement IN ('entree', 'sortie')),
                quantite REAL NOT NULL CHECK (quantite > 0),
                bande_id INTEGER,
                motif TEXT,
                FOREIGN KEY (stock_id) REFERENCES stocks(id),
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        self._create_stock_indexes()

    def _create_stock_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_mouvements_stock_stock_date "
            "ON mouvements_stock (stock_id, date)"
        )

    def _migration_6_sanitaire(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions_sanitaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                type_intervention TEXT NOT NULL
                    CHECK (type_intervention IN ('vaccination', 'traitement')),
                produit TEXT NOT NULL,
                dose TEXT,
                intervenant TEXT,
                prochaine_echeance DATE,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interventions_bande_date "
            "ON interventions_sanitaires (bande_id, date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_interventions_echeance "
            "ON interventions_sanitaires (prochaine_echeance)"
        )

    def _ensure_column(self, table, column, definition):
        cursor = self.conn.cursor()
        columns = {
            row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _create_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_mortalites_bande_date "
            "ON mortalites (bande_id, date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_depenses_bande_date "
            "ON depenses (bande_id, date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_ventes_bande_date "
            "ON ventes (bande_id, date)"
        )

    def _create_zootechnie_indexes(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_consommations_aliment_bande_date "
            "ON consommations_aliment (bande_id, date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pesees_bande_date "
            "ON pesees (bande_id, date)"
        )

    def ajouter_bande(
        self, nom_bande, date_debut, nombre_initial, prix_achat=None,
        activite='chair'
    ):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO bandes (
                nom_bande, date_debut, nombre_initial, prix_achat_poussin, activite
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (nom_bande, date_debut, nombre_initial, prix_achat, activite))
        self.conn.commit()
        return cursor.lastrowid

    def modifier_bande(
        self, bande_id, nom_bande, date_debut, nombre_initial, prix_achat=None
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            UPDATE bandes
            SET nom_bande = ?, date_debut = ?, nombre_initial = ?,
                prix_achat_poussin = ?
            WHERE id = ?
            ''',
            (nom_bande, date_debut, nombre_initial, prix_achat, bande_id),
        )
        self.conn.commit()

    def cloturer_bande(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE bandes SET statut = 'cloture' WHERE id = ?", (bande_id,)
        )
        self.conn.commit()

    def ajouter_mortalite(
        self, bande_id, date, nombre_morts, cause=None, description=None
    ):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO mortalites (bande_id, date, nombre_morts, cause, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (bande_id, date, nombre_morts, cause, description))
        self.conn.commit()

    def get_mortalites(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, nombre_morts, cause, description
            FROM mortalites
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def ajouter_depense(self, bande_id, date, type_depense, montant, description=None, fournisseur=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO depenses (bande_id, date, type_depense, montant, description, fournisseur)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bande_id, date, type_depense, montant, description, fournisseur))
        self.conn.commit()

    def get_depenses(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, type_depense, description, montant, fournisseur
            FROM depenses
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def ajouter_consommation_aliment(
        self, bande_id, date, quantite_kg, type_aliment=None, observation=None
    ):
        if quantite_kg <= 0:
            raise ValueError("La quantite d'aliment doit etre superieure a zero.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO consommations_aliment (
                bande_id, date, quantite_kg, type_aliment, observation
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (bande_id, date, quantite_kg, type_aliment, observation))
        self.conn.commit()

    def ajouter_pesee(
        self, bande_id, date, poids_moyen_g, effectif_pese, observation=None
    ):
        if poids_moyen_g <= 0:
            raise ValueError("Le poids moyen doit etre superieur a zero.")
        if effectif_pese <= 0:
            raise ValueError("L'effectif pese doit etre superieur a zero.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO pesees (
                bande_id, date, poids_moyen_g, effectif_pese, observation
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (bande_id, date, poids_moyen_g, effectif_pese, observation))
        self.conn.commit()

    def ajouter_ponte(self, bande_id, date, nombre_oeufs, observation=None):
        if nombre_oeufs <= 0:
            raise ValueError("Le nombre d'oeufs doit etre superieur a zero.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO pontes (bande_id, date, nombre_oeufs, observation)
            VALUES (?, ?, ?, ?)
        ''', (bande_id, date, nombre_oeufs, observation))
        cursor.execute('''
            INSERT INTO mouvements_oeufs (bande_id, date, type_mouvement, quantite)
            VALUES (?, ?, 'entree_production', ?)
        ''', (bande_id, date, nombre_oeufs))
        self.conn.commit()

    def get_total_oeufs(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT SUM(nombre_oeufs) FROM pontes WHERE bande_id = ?', (bande_id,)
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_nombre_jours_ponte(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT COUNT(DISTINCT date) FROM pontes WHERE bande_id = ?',
            (bande_id,),
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_pontes(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, nombre_oeufs, observation
            FROM pontes
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_stock_oeufs(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT COALESCE(SUM(
                CASE WHEN type_mouvement = 'entree_production'
                     THEN quantite ELSE -quantite END
            ), 0)
            FROM mouvements_oeufs WHERE bande_id = ?
            ''',
            (bande_id,),
        )
        return cursor.fetchone()[0]

    def ajouter_vente_oeufs(
        self, bande_id, date, quantite, prix_unitaire, client=None
    ):
        if quantite <= 0:
            raise ValueError("La quantite vendue doit etre superieure a zero.")
        stock = self.get_stock_oeufs(bande_id)
        if quantite > stock:
            raise ValueError(
                f"Vente refusée : {quantite} œufs demandés pour {stock} en stock."
            )
        montant = quantite * prix_unitaire
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO mouvements_oeufs (
                bande_id, date, type_mouvement, quantite, prix_unitaire,
                montant, client
            )
            VALUES (?, ?, 'vente', ?, ?, ?, ?)
        ''', (bande_id, date, quantite, prix_unitaire, montant, client))
        self.conn.commit()

    def get_ventes_oeufs(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, quantite, prix_unitaire, montant, client
            FROM mouvements_oeufs
            WHERE type_mouvement = 'vente'
        '''
        params = ()
        if bande_id is not None:
            query += ' AND bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_total_ventes_oeufs(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT SUM(montant) FROM mouvements_oeufs
            WHERE bande_id = ? AND type_mouvement = 'vente'
            ''',
            (bande_id,),
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def ajouter_vente(
        self, bande_id, date, nombre_poulets, prix_unitaire, client=None,
        paiement=None, poids_total=None
    ):
        restants = self.get_poulets_restants(bande_id)
        if nombre_poulets > restants:
            raise ValueError(
                f"Vente refusée : {nombre_poulets} sujets demandés pour "
                f"{restants} disponibles."
            )
        if poids_total is not None and poids_total < 0:
            raise ValueError("Le poids total vendu ne peut pas être négatif.")
        montant_total = nombre_poulets * prix_unitaire
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO ventes (
                bande_id, date, nombre_poulets, prix_unitaire, montant_total,
                client, paiement, poids_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bande_id, date, nombre_poulets, prix_unitaire, montant_total,
            client, paiement, poids_total
        ))
        self.conn.commit()

    def get_bande_info(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM bandes WHERE id = ?', (bande_id,))
        return cursor.fetchone()

    def get_total_mortalites(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(nombre_morts) FROM mortalites WHERE bande_id = ?', (bande_id,))
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_total_depenses(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(montant) FROM depenses WHERE bande_id = ?', (bande_id,))
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_cout_initial(self, bande_id):
        bande = self.get_bande_info(bande_id)
        if not bande:
            return 0
        nombre_initial = bande[3] or 0
        prix_achat = bande[4] or 0
        return nombre_initial * prix_achat

    def get_total_couts(self, bande_id):
        return self.get_cout_initial(bande_id) + self.get_total_depenses(bande_id)

    def get_total_ventes(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(montant_total) FROM ventes WHERE bande_id = ?', (bande_id,))
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_poulets_restants(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT nombre_initial FROM bandes WHERE id = ?', (bande_id,))
        row = cursor.fetchone()
        if not row:
            return 0
        initial = row[0]
        total_morts = self.get_total_mortalites(bande_id)
        total_vendus = self.get_total_vendus(bande_id)
        return initial - total_morts - total_vendus

    def get_total_vendus(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(nombre_poulets) FROM ventes WHERE bande_id = ?', (bande_id,))
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_total_poids_vendu(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT SUM(poids_total) FROM ventes WHERE bande_id = ?', (bande_id,)
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_total_aliment_kg(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT SUM(quantite_kg) FROM consommations_aliment WHERE bande_id = ?',
            (bande_id,),
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_consommations_aliment(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, quantite_kg, type_aliment, observation
            FROM consommations_aliment
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_pesees(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, poids_moyen_g, effectif_pese, observation
            FROM pesees
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_latest_pesee(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, bande_id, date, poids_moyen_g, effectif_pese, observation
            FROM pesees
            WHERE bande_id = ?
            ORDER BY date DESC, id DESC
            LIMIT 1
            ''',
            (bande_id,),
        )
        return cursor.fetchone()

    def get_first_pesee(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, bande_id, date, poids_moyen_g, effectif_pese, observation
            FROM pesees
            WHERE bande_id = ?
            ORDER BY date ASC, id ASC
            LIMIT 1
            ''',
            (bande_id,),
        )
        return cursor.fetchone()

    def get_bandes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM bandes ORDER BY date_debut DESC')
        return cursor.fetchall()

    def ajouter_article_stock(self, nom_article, categorie, unite, seuil_alerte=0):
        if categorie not in ('aliment', 'medicament', 'litiere'):
            raise ValueError("Catégorie de stock invalide.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO stocks (nom_article, categorie, unite, seuil_alerte)
            VALUES (?, ?, ?, ?)
        ''', (nom_article, categorie, unite, seuil_alerte))
        self.conn.commit()
        return cursor.lastrowid

    def get_articles_stock(self):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, nom_article, categorie, unite, seuil_alerte '
            'FROM stocks ORDER BY categorie, nom_article'
        )
        return cursor.fetchall()

    def get_stock_quantite(self, stock_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT COALESCE(SUM(
                CASE WHEN type_mouvement = 'entree' THEN quantite ELSE -quantite END
            ), 0)
            FROM mouvements_stock WHERE stock_id = ?
            ''',
            (stock_id,),
        )
        return cursor.fetchone()[0]

    def ajouter_mouvement_stock(
        self, stock_id, date, type_mouvement, quantite, bande_id=None, motif=None
    ):
        if type_mouvement not in ('entree', 'sortie'):
            raise ValueError("Type de mouvement invalide.")
        if quantite <= 0:
            raise ValueError("La quantité doit être supérieure à zéro.")
        if type_mouvement == 'sortie':
            stock_actuel = self.get_stock_quantite(stock_id)
            if quantite > stock_actuel:
                raise ValueError(
                    f"Sortie refusée : {quantite:g} demandé(s) pour "
                    f"{stock_actuel:g} en stock."
                )
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO mouvements_stock (
                stock_id, date, type_mouvement, quantite, bande_id, motif
            )
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (stock_id, date, type_mouvement, quantite, bande_id, motif))
        self.conn.commit()

    def get_mouvements_stock(self, stock_id=None, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, stock_id, date, type_mouvement, quantite, bande_id, motif
            FROM mouvements_stock
        '''
        filters = []
        params = []
        if stock_id is not None:
            filters.append('stock_id = ?')
            params.append(stock_id)
        if bande_id is not None:
            filters.append('bande_id = ?')
            params.append(bande_id)
        if filters:
            query += ' WHERE ' + ' AND '.join(filters)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    def get_mouvements_stock_par_bande(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT m.id, m.stock_id, m.date, m.type_mouvement, m.quantite,
                   m.bande_id, m.motif, s.nom_article, s.categorie, s.unite
            FROM mouvements_stock m
            JOIN stocks s ON s.id = m.stock_id
            WHERE m.bande_id = ?
            ORDER BY m.date DESC, m.id DESC
            ''',
            (bande_id,),
        )
        return cursor.fetchall()

    def get_articles_sous_seuil(self):
        return [
            article
            for article in self.get_articles_stock()
            if self.get_stock_quantite(article[0]) < article[4]
        ]

    def ajouter_sortie_stock_aliment(
        self, stock_id, bande_id, date, quantite_kg, type_aliment=None,
        observation=None
    ):
        """EF-6.4 : une sortie de stock d'aliment credite aussi
        consommations_aliment, pour eviter la double saisie entre le module
        Stocks et le suivi zootechnique (IC, Phase 2)."""
        if quantite_kg <= 0:
            raise ValueError("La quantité d'aliment doit être supérieure à zéro.")
        stock_actuel = self.get_stock_quantite(stock_id)
        if quantite_kg > stock_actuel:
            raise ValueError(
                f"Sortie refusée : {quantite_kg:g} kg demandés pour "
                f"{stock_actuel:g} kg en stock."
            )
        cursor = self.conn.cursor()
        motif = (
            f"Consommation aliment - {observation}"
            if observation else "Consommation aliment"
        )
        cursor.execute('''
            INSERT INTO mouvements_stock (
                stock_id, date, type_mouvement, quantite, bande_id, motif
            )
            VALUES (?, ?, 'sortie', ?, ?, ?)
        ''', (stock_id, date, quantite_kg, bande_id, motif))
        cursor.execute('''
            INSERT INTO consommations_aliment (
                bande_id, date, quantite_kg, type_aliment, observation
            )
            VALUES (?, ?, ?, ?, ?)
        ''', (bande_id, date, quantite_kg, type_aliment, observation))
        self.conn.commit()

    def ajouter_intervention_sanitaire(
        self, bande_id, date, type_intervention, produit, dose=None,
        intervenant=None, prochaine_echeance=None
    ):
        if type_intervention not in ('vaccination', 'traitement'):
            raise ValueError("Type d'intervention invalide.")
        if not produit:
            raise ValueError("Le produit est obligatoire.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO interventions_sanitaires (
                bande_id, date, type_intervention, produit, dose, intervenant,
                prochaine_echeance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            bande_id, date, type_intervention, produit, dose, intervenant,
            prochaine_echeance
        ))
        self.conn.commit()

    def get_ventes(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, nombre_poulets, prix_unitaire,
                   montant_total, client, paiement, poids_total
            FROM ventes
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_interventions_sanitaires(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, type_intervention, produit, dose,
                   intervenant, prochaine_echeance
            FROM interventions_sanitaires
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_interventions_a_venir(self, date_reference):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, bande_id, date, type_intervention, produit, dose,
                   intervenant, prochaine_echeance
            FROM interventions_sanitaires
            WHERE prochaine_echeance IS NOT NULL AND prochaine_echeance >= ?
            ORDER BY prochaine_echeance ASC, id ASC
            ''',
            (date_reference,),
        )
        return cursor.fetchall()

    def get_rentabilite_par_activite(self):
        resultat = {
            'chair': {'recettes': 0, 'couts': 0, 'benefice': 0, 'nb_lots': 0},
            'ponte': {'recettes': 0, 'couts': 0, 'benefice': 0, 'nb_lots': 0},
        }
        for bande in self.get_bandes():
            bande_id = bande[0]
            activite = bande[6] if len(bande) > 6 and bande[6] else 'chair'
            if activite not in resultat:
                activite = 'chair'

            couts = self.get_total_couts(bande_id)
            recettes = (
                self.get_total_ventes_oeufs(bande_id)
                if activite == 'ponte'
                else self.get_total_ventes(bande_id)
            )
            resultat[activite]['recettes'] += recettes
            resultat[activite]['couts'] += couts
            resultat[activite]['benefice'] += recettes - couts
            resultat[activite]['nb_lots'] += 1
        return resultat

    def get_fiche_lot_agasa(self, bande_id):
        import reporting

        return reporting.build_fiche_lot_agasa(self, bande_id)

    def get_synthese_direction(self, date_reference=None):
        import reporting

        return reporting.build_synthese_direction(self, date_reference)

    def close(self):
        self.conn.close()
