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

    SCHEMA_VERSION = 10

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
        elif version == 7:
            self._migration_7_previsions()
        elif version == 8:
            self._migration_8_journal_actions()
        elif version == 9:
            self._migration_9_calibrage_oeufs()
        elif version == 10:
            self._migration_10_hors_perimetre_v2()

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

    def _migration_7_previsions(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS previsions_lot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL UNIQUE,
                cout_poussins_prevu REAL NOT NULL DEFAULT 0
                    CHECK (cout_poussins_prevu >= 0),
                cout_aliment_prevu REAL NOT NULL DEFAULT 0
                    CHECK (cout_aliment_prevu >= 0),
                cout_sanitaire_prevu REAL NOT NULL DEFAULT 0
                    CHECK (cout_sanitaire_prevu >= 0),
                autres_charges_prevues REAL NOT NULL DEFAULT 0
                    CHECK (autres_charges_prevues >= 0),
                quantite_vendue_prevue REAL NOT NULL DEFAULT 0
                    CHECK (quantite_vendue_prevue >= 0),
                prix_vente_unitaire_prevu REAL NOT NULL DEFAULT 0
                    CHECK (prix_vente_unitaire_prevu >= 0),
                oeufs_prevus INTEGER NOT NULL DEFAULT 0
                    CHECK (oeufs_prevus >= 0),
                prix_oeuf_prevu REAL NOT NULL DEFAULT 0
                    CHECK (prix_oeuf_prevu >= 0),
                note TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (bande_id) REFERENCES bandes(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_previsions_lot_bande "
            "ON previsions_lot (bande_id)"
        )

    def _migration_8_journal_actions(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_action TEXT NOT NULL,
                action TEXT NOT NULL,
                entite TEXT NOT NULL,
                entite_id INTEGER,
                detail TEXT
            )
        ''')
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_journal_actions_date "
            "ON journal_actions (date_action)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_journal_actions_entite "
            "ON journal_actions (entite, entite_id)"
        )

    def _migration_9_calibrage_oeufs(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calibrages_oeufs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                categorie TEXT NOT NULL
                    CHECK (categorie IN (
                        'petit', 'moyen', 'gros', 'tres_gros', 'declasse'
                    )),
                quantite INTEGER NOT NULL CHECK (quantite > 0),
                poids_moyen_g REAL CHECK (
                    poids_moyen_g IS NULL OR poids_moyen_g > 0
                ),
                observation TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_calibrages_oeufs_bande_date "
            "ON calibrages_oeufs (bande_id, date)"
        )

    def _migration_10_hors_perimetre_v2(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='pontes'"
        )
        row = cursor.fetchone()
        if row and "nombre_oeufs > 0" in (row[0] or ""):
            cursor.execute("ALTER TABLE pontes RENAME TO pontes_v9")
            cursor.execute('''
                CREATE TABLE pontes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bande_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    nombre_oeufs INTEGER NOT NULL CHECK (nombre_oeufs >= 0),
                    observation TEXT,
                    FOREIGN KEY (bande_id) REFERENCES bandes(id)
                )
            ''')
            cursor.execute('''
                INSERT INTO pontes (id, bande_id, date, nombre_oeufs, observation)
                SELECT id, bande_id, date, nombre_oeufs, observation
                FROM pontes_v9
            ''')
            cursor.execute("DROP TABLE pontes_v9")
            self._create_ponte_indexes()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sorties_effectif (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bande_id INTEGER NOT NULL,
                date DATE NOT NULL,
                nombre INTEGER NOT NULL CHECK (nombre > 0),
                motif TEXT,
                description TEXT,
                FOREIGN KEY (bande_id) REFERENCES bandes(id)
            )
        ''')
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sorties_effectif_bande_date "
            "ON sorties_effectif (bande_id, date)"
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

    def _log_action(self, action, entite, entite_id=None, detail=None, cursor=None):
        active_cursor = cursor or self.conn.cursor()
        active_cursor.execute(
            '''
            INSERT INTO journal_actions (
                date_action, action, entite, entite_id, detail
            )
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                datetime.now().isoformat(timespec="seconds"),
                action,
                entite,
                entite_id,
                detail,
            ),
        )

    def enregistrer_action(self, action, entite, entite_id=None, detail=None):
        self._log_action(action, entite, entite_id, detail)
        self.conn.commit()

    def get_journal_actions(self, limit=None, action=None, entite=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, date_action, action, entite, entite_id, detail
            FROM journal_actions
        '''
        filters = []
        params = []
        if action is not None:
            filters.append('action = ?')
            params.append(action)
        if entite is not None:
            filters.append('entite = ?')
            params.append(entite)
        if filters:
            query += ' WHERE ' + ' AND '.join(filters)
        query += ' ORDER BY date_action DESC, id DESC'
        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

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
        bande_id = cursor.lastrowid
        self._log_action(
            'creation_bande',
            'bandes',
            bande_id,
            f"{nom_bande} ({activite}) - effectif {nombre_initial}",
            cursor,
        )
        self.conn.commit()
        return bande_id

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
        self._log_action(
            'modification_bande',
            'bandes',
            bande_id,
            f"{nom_bande} - effectif {nombre_initial}",
            cursor,
        )
        self.conn.commit()

    def cloturer_bande(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE bandes SET statut = 'cloture' WHERE id = ?", (bande_id,)
        )
        self._log_action('cloture_bande', 'bandes', bande_id, cursor=cursor)
        self.conn.commit()

    def ajouter_mortalite(
        self, bande_id, date, nombre_morts, cause=None, description=None
    ):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO mortalites (bande_id, date, nombre_morts, cause, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (bande_id, date, nombre_morts, cause, description))
        self._log_action(
            'mortalite',
            'mortalites',
            cursor.lastrowid,
            f"{nombre_morts} morts - {cause or 'cause non renseignee'}",
            cursor,
        )
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
        self._log_action(
            'depense',
            'depenses',
            cursor.lastrowid,
            f"{type_depense} - {montant:.0f} FCFA",
            cursor,
        )
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
        self.enregistrer_consommation_aliment(
            bande_id, date, quantite_kg, type_aliment, observation
        )

    def enregistrer_consommation_aliment(
        self, bande_id, date, quantite_kg, type_aliment=None, observation=None,
        stock_id=None
    ):
        if quantite_kg <= 0:
            raise ValueError("La quantite d'aliment doit etre superieure a zero.")
        stock_info = None
        if stock_id is not None:
            stock_info = self._get_article_stock_info(stock_id)
            if stock_info is None:
                raise ValueError(f"Article de stock introuvable (id={stock_id}).")
            if stock_info[2] != 'aliment':
                raise ValueError("Seuls les articles de stock aliment peuvent etre lies.")
            stock_actuel = self.get_stock_quantite(stock_id)
            if quantite_kg > stock_actuel:
                raise ValueError(
                    f"Sortie refusee : {quantite_kg:g} kg demandes pour "
                    f"{stock_actuel:g} kg en stock."
                )
        cursor = self.conn.cursor()
        try:
            mouvement_id = None
            if stock_id is not None:
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
                mouvement_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO consommations_aliment (
                    bande_id, date, quantite_kg, type_aliment, observation
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (bande_id, date, quantite_kg, type_aliment, observation))
            consommation_id = cursor.lastrowid
            if stock_id is not None:
                self._log_action(
                    'sortie_stock_aliment',
                    'mouvements_stock',
                    mouvement_id,
                    f"{quantite_kg:g} kg - stock #{stock_id}",
                    cursor,
                )
            else:
                self._log_action(
                    'consommation_aliment',
                    'consommations_aliment',
                    consommation_id,
                    f"{quantite_kg:g} kg - {type_aliment or 'type non renseigne'}",
                    cursor,
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

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
        self._log_action(
            'pesee',
            'pesees',
            cursor.lastrowid,
            f"{poids_moyen_g:g} g sur {effectif_pese} sujets",
            cursor,
        )
        self.conn.commit()

    def ajouter_ponte(self, bande_id, date, nombre_oeufs, observation=None):
        if nombre_oeufs < 0:
            raise ValueError("Le nombre d'oeufs ne peut pas etre negatif.")
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pontes (bande_id, date, nombre_oeufs, observation)
                VALUES (?, ?, ?, ?)
            ''', (bande_id, date, nombre_oeufs, observation))
            ponte_id = cursor.lastrowid
            if nombre_oeufs > 0:
                cursor.execute('''
                    INSERT INTO mouvements_oeufs (
                        bande_id, date, type_mouvement, quantite
                    )
                    VALUES (?, ?, 'entree_production', ?)
                ''', (bande_id, date, nombre_oeufs))
            self._log_action(
                'ponte',
                'pontes',
                ponte_id,
                f"{nombre_oeufs} oeufs produits",
                cursor,
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

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

    CATEGORIES_CALIBRAGE_OEUFS = {
        'petit', 'moyen', 'gros', 'tres_gros', 'declasse'
    }

    def ajouter_calibrage_oeufs(
        self, bande_id, date, categorie, quantite, poids_moyen_g=None,
        observation=None
    ):
        if categorie not in self.CATEGORIES_CALIBRAGE_OEUFS:
            raise ValueError("Categorie de calibrage invalide.")
        if quantite <= 0:
            raise ValueError("La quantite calibree doit etre superieure a zero.")
        if poids_moyen_g is not None and poids_moyen_g <= 0:
            raise ValueError("Le poids moyen doit etre superieur a zero.")
        deja_calibres = self.get_total_oeufs_calibres(bande_id)
        total_produits = self.get_total_oeufs(bande_id)
        if deja_calibres + quantite > total_produits:
            raise ValueError(
                "Calibrage refuse : la quantite calibree depasse la production."
            )
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            INSERT INTO calibrages_oeufs (
                bande_id, date, categorie, quantite, poids_moyen_g, observation
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (bande_id, date, categorie, quantite, poids_moyen_g, observation),
        )
        self._log_action(
            'calibrage_oeufs',
            'calibrages_oeufs',
            cursor.lastrowid,
            f"{quantite} oeufs calibres - {categorie}",
            cursor,
        )
        self.conn.commit()

    def get_calibrages_oeufs(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, categorie, quantite, poids_moyen_g,
                   observation
            FROM calibrages_oeufs
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_total_oeufs_calibres(self, bande_id=None):
        cursor = self.conn.cursor()
        query = 'SELECT SUM(quantite) FROM calibrages_oeufs'
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        cursor.execute(query, params)
        result = cursor.fetchone()[0]
        return result if result else 0

    def get_calibrage_oeufs_par_categorie(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT categorie, SUM(quantite)
            FROM calibrages_oeufs
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' GROUP BY categorie ORDER BY categorie'
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
        self._log_action(
            'vente_oeufs',
            'mouvements_oeufs',
            cursor.lastrowid,
            f"{quantite} oeufs vendus pour {montant:.0f} FCFA",
            cursor,
        )
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
        self._log_action(
            'vente_poulets',
            'ventes',
            cursor.lastrowid,
            f"{nombre_poulets} sujets vendus pour {montant_total:.0f} FCFA",
            cursor,
        )
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

    def ajouter_sortie_effectif(
        self, bande_id, date, nombre, motif=None, description=None
    ):
        if nombre <= 0:
            raise ValueError("La sortie d'effectif doit etre superieure a zero.")
        restants = self.get_poulets_restants(bande_id)
        if nombre > restants:
            raise ValueError(
                f"Sortie refusee : {nombre} sujets demandes pour "
                f"{restants} disponibles."
            )
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            INSERT INTO sorties_effectif (
                bande_id, date, nombre, motif, description
            )
            VALUES (?, ?, ?, ?, ?)
            ''',
            (bande_id, date, nombre, motif, description),
        )
        sortie_id = cursor.lastrowid
        self._log_action(
            'sortie_effectif',
            'sorties_effectif',
            sortie_id,
            f"{nombre} sujets sortis - {motif or 'motif non renseigne'}",
            cursor,
        )
        self.conn.commit()

    def get_sorties_effectif(self, bande_id=None):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, bande_id, date, nombre, motif, description
            FROM sorties_effectif
        '''
        params = ()
        if bande_id is not None:
            query += ' WHERE bande_id = ?'
            params = (bande_id,)
        query += ' ORDER BY date DESC, id DESC'
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_total_sorties_effectif(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT SUM(nombre) FROM sorties_effectif WHERE bande_id = ?',
            (bande_id,),
        )
        result = cursor.fetchone()[0]
        return result if result else 0

    def supprimer_sortie_effectif(self, sortie_id):
        self._supprimer_enregistrement(
            "sorties_effectif",
            sortie_id,
            "suppression_sortie_effectif",
            "Sortie d'effectif",
        )

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
        total_sorties = self.get_total_sorties_effectif(bande_id)
        return initial - total_morts - total_vendus - total_sorties

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

    def _supprimer_enregistrement(self, table, record_id, action, libelle):
        """Suppression generique tracee dans le journal d'actions."""
        cursor = self.conn.cursor()
        row = cursor.execute(
            f"SELECT id FROM {table} WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"{libelle} introuvable (id={record_id}).")
        try:
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
            self._log_action(
                action, table, record_id, f"{libelle} supprime(e)", cursor
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def supprimer_mortalite(self, mortalite_id):
        self._supprimer_enregistrement(
            "mortalites", mortalite_id, "suppression_mortalite", "Mortalite"
        )

    def supprimer_depense(self, depense_id):
        self._supprimer_enregistrement(
            "depenses", depense_id, "suppression_depense", "Depense"
        )

    def supprimer_vente(self, vente_id):
        self._supprimer_enregistrement(
            "ventes", vente_id, "suppression_vente", "Vente"
        )

    def supprimer_consommation_aliment(self, consommation_id):
        self._supprimer_enregistrement(
            "consommations_aliment", consommation_id,
            "suppression_consommation_aliment", "Consommation d'aliment"
        )

    def supprimer_pesee(self, pesee_id):
        self._supprimer_enregistrement(
            "pesees", pesee_id, "suppression_pesee", "Pesee"
        )

    def supprimer_ponte(self, ponte_id):
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT bande_id, date, nombre_oeufs FROM pontes WHERE id = ?",
            (ponte_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Ponte introuvable (id={ponte_id}).")
        bande_id, date_ponte, nombre_oeufs = row
        if self.get_stock_oeufs(bande_id) - nombre_oeufs < 0:
            raise ValueError(
                "Suppression refusee : des oeufs de cette production "
                "ont deja ete vendus."
            )
        production_restante = self.get_total_oeufs(bande_id) - nombre_oeufs
        if self.get_total_oeufs_calibres(bande_id) > production_restante:
            raise ValueError(
                "Suppression refusee : la production restante serait "
                "inferieure aux oeufs deja calibres."
            )
        try:
            cursor.execute("DELETE FROM pontes WHERE id = ?", (ponte_id,))
            cursor.execute(
                '''
                DELETE FROM mouvements_oeufs WHERE id = (
                    SELECT id FROM mouvements_oeufs
                    WHERE bande_id = ? AND date = ?
                          AND type_mouvement = 'entree_production'
                          AND quantite = ?
                    ORDER BY id DESC
                    LIMIT 1
                )
                ''',
                (bande_id, date_ponte, nombre_oeufs),
            )
            self._log_action(
                "suppression_ponte",
                "pontes",
                ponte_id,
                f"{nombre_oeufs} oeufs annules",
                cursor,
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def supprimer_vente_oeufs(self, mouvement_id):
        cursor = self.conn.cursor()
        row = cursor.execute(
            "SELECT quantite, montant FROM mouvements_oeufs "
            "WHERE id = ? AND type_mouvement = 'vente'",
            (mouvement_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Vente d'oeufs introuvable (id={mouvement_id}).")
        try:
            cursor.execute(
                "DELETE FROM mouvements_oeufs WHERE id = ?", (mouvement_id,)
            )
            self._log_action(
                "suppression_vente_oeufs",
                "mouvements_oeufs",
                mouvement_id,
                f"vente de {row[0]} oeufs annulee ({row[1]:.0f} FCFA)",
                cursor,
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def get_derniere_date_saisie(self, bande_id):
        """Date ISO de la saisie la plus recente du lot, ou None."""
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT MAX(d) FROM (
                SELECT MAX(date) AS d FROM mortalites WHERE bande_id = :b
                UNION ALL
                SELECT MAX(date) FROM consommations_aliment WHERE bande_id = :b
                UNION ALL
                SELECT MAX(date) FROM pesees WHERE bande_id = :b
                UNION ALL
                SELECT MAX(date) FROM pontes WHERE bande_id = :b
                UNION ALL
                SELECT MAX(date) FROM ventes WHERE bande_id = :b
                UNION ALL
                SELECT MAX(date) FROM depenses WHERE bande_id = :b
            )
            ''',
            {"b": bande_id},
        )
        return cursor.fetchone()[0]

    def compter_saisies_du_jour(self, bande_id, date):
        """Nombre de saisies deja enregistrees ce jour-la, par famille."""
        cursor = self.conn.cursor()
        resultat = {}
        for cle, table in (
            ("mortalites", "mortalites"),
            ("aliment", "consommations_aliment"),
            ("pontes", "pontes"),
        ):
            cursor.execute(
                f"SELECT COUNT(*) FROM {table} WHERE bande_id = ? AND date = ?",
                (bande_id, date),
            )
            resultat[cle] = cursor.fetchone()[0]
        return resultat

    def enregistrer_saisie_journaliere(
        self, bande_id, date, morts=None, cause=None,
        aliment_kg=None, type_aliment=None, oeufs=None, observation=None
    ):
        """Enregistre mortalite, aliment et oeufs en une transaction."""
        if not any((morts, aliment_kg)) and oeufs is None:
            raise ValueError(
                "Renseignez au moins une valeur (morts, aliment ou oeufs)."
            )
        if morts:
            restants = self.get_poulets_restants(bande_id)
            if morts < 0 or morts > restants:
                raise ValueError(
                    f"Mortalite invalide : {restants} sujets disponibles."
                )
        if aliment_kg is not None and aliment_kg <= 0:
            raise ValueError(
                "La quantite d'aliment doit etre superieure a zero."
            )
        if oeufs is not None and oeufs < 0:
            raise ValueError("Le nombre d'oeufs ne peut pas etre negatif.")

        cursor = self.conn.cursor()
        try:
            if morts:
                cursor.execute(
                    '''
                    INSERT INTO mortalites (
                        bande_id, date, nombre_morts, cause, description
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (bande_id, date, morts, cause, observation),
                )
            if aliment_kg:
                cursor.execute(
                    '''
                    INSERT INTO consommations_aliment (
                        bande_id, date, quantite_kg, type_aliment, observation
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (bande_id, date, aliment_kg, type_aliment, observation),
                )
            if oeufs is not None:
                cursor.execute(
                    '''
                    INSERT INTO pontes (bande_id, date, nombre_oeufs, observation)
                    VALUES (?, ?, ?, ?)
                    ''',
                    (bande_id, date, oeufs, observation),
                )
                if oeufs > 0:
                    cursor.execute(
                        '''
                        INSERT INTO mouvements_oeufs (
                            bande_id, date, type_mouvement, quantite
                        )
                        VALUES (?, ?, 'entree_production', ?)
                        ''',
                        (bande_id, date, oeufs),
                    )
            self._log_action(
                "saisie_journaliere",
                "bandes",
                bande_id,
                f"morts={morts or 0}, aliment={aliment_kg or 0} kg, "
                f"oeufs={oeufs or 0}",
                cursor,
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

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

    def enregistrer_prevision_lot(
        self, bande_id, cout_poussins_prevu=0, cout_aliment_prevu=0,
        cout_sanitaire_prevu=0, autres_charges_prevues=0,
        quantite_vendue_prevue=0, prix_vente_unitaire_prevu=0,
        oeufs_prevus=0, prix_oeuf_prevu=0, note=None
    ):
        values = {
            'cout_poussins_prevu': cout_poussins_prevu,
            'cout_aliment_prevu': cout_aliment_prevu,
            'cout_sanitaire_prevu': cout_sanitaire_prevu,
            'autres_charges_prevues': autres_charges_prevues,
            'quantite_vendue_prevue': quantite_vendue_prevue,
            'prix_vente_unitaire_prevu': prix_vente_unitaire_prevu,
            'oeufs_prevus': oeufs_prevus,
            'prix_oeuf_prevu': prix_oeuf_prevu,
        }
        if any((value or 0) < 0 for value in values.values()):
            raise ValueError("Les previsions ne peuvent pas etre negatives.")
        updated_at = datetime.now().isoformat(timespec="seconds")
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            INSERT INTO previsions_lot (
                bande_id, cout_poussins_prevu, cout_aliment_prevu,
                cout_sanitaire_prevu, autres_charges_prevues,
                quantite_vendue_prevue, prix_vente_unitaire_prevu,
                oeufs_prevus, prix_oeuf_prevu, note, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bande_id) DO UPDATE SET
                cout_poussins_prevu = excluded.cout_poussins_prevu,
                cout_aliment_prevu = excluded.cout_aliment_prevu,
                cout_sanitaire_prevu = excluded.cout_sanitaire_prevu,
                autres_charges_prevues = excluded.autres_charges_prevues,
                quantite_vendue_prevue = excluded.quantite_vendue_prevue,
                prix_vente_unitaire_prevu = excluded.prix_vente_unitaire_prevu,
                oeufs_prevus = excluded.oeufs_prevus,
                prix_oeuf_prevu = excluded.prix_oeuf_prevu,
                note = excluded.note,
                updated_at = excluded.updated_at
            ''',
            (
                bande_id,
                cout_poussins_prevu or 0,
                cout_aliment_prevu or 0,
                cout_sanitaire_prevu or 0,
                autres_charges_prevues or 0,
                quantite_vendue_prevue or 0,
                prix_vente_unitaire_prevu or 0,
                int(oeufs_prevus or 0),
                prix_oeuf_prevu or 0,
                note,
                updated_at,
            ),
        )
        self._log_action(
            'prevision_lot',
            'previsions_lot',
            bande_id,
            "Previsions du lot mises a jour",
            cursor,
        )
        self.conn.commit()

    def get_prevision_lot(self, bande_id):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, bande_id, cout_poussins_prevu, cout_aliment_prevu,
                   cout_sanitaire_prevu, autres_charges_prevues,
                   quantite_vendue_prevue, prix_vente_unitaire_prevu,
                   oeufs_prevus, prix_oeuf_prevu, note, updated_at
            FROM previsions_lot
            WHERE bande_id = ?
            ''',
            (bande_id,),
        )
        return cursor.fetchone()

    def get_previsions_lots(self):
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, bande_id, cout_poussins_prevu, cout_aliment_prevu,
                   cout_sanitaire_prevu, autres_charges_prevues,
                   quantite_vendue_prevue, prix_vente_unitaire_prevu,
                   oeufs_prevus, prix_oeuf_prevu, note, updated_at
            FROM previsions_lot
            ORDER BY bande_id ASC
            '''
        )
        return cursor.fetchall()

    def ajouter_article_stock(self, nom_article, categorie, unite, seuil_alerte=0):
        if categorie not in ('aliment', 'medicament', 'litiere'):
            raise ValueError("Catégorie de stock invalide.")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO stocks (nom_article, categorie, unite, seuil_alerte)
            VALUES (?, ?, ?, ?)
        ''', (nom_article, categorie, unite, seuil_alerte))
        stock_id = cursor.lastrowid
        self._log_action(
            'creation_stock',
            'stocks',
            stock_id,
            f"{nom_article} ({categorie})",
            cursor,
        )
        self.conn.commit()
        return stock_id

    def get_articles_stock(self):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, nom_article, categorie, unite, seuil_alerte '
            'FROM stocks ORDER BY categorie, nom_article'
        )
        return cursor.fetchall()

    def _get_article_stock_info(self, stock_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, nom_article, categorie, unite, seuil_alerte '
            'FROM stocks WHERE id = ?',
            (stock_id,),
        )
        return cursor.fetchone()

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
        self._log_action(
            'mouvement_stock',
            'mouvements_stock',
            cursor.lastrowid,
            f"{type_mouvement} {quantite:g} - stock #{stock_id}",
            cursor,
        )
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
        self.enregistrer_consommation_aliment(
            bande_id,
            date,
            quantite_kg,
            type_aliment,
            observation,
            stock_id,
        )

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
        self._log_action(
            'intervention_sanitaire',
            'interventions_sanitaires',
            cursor.lastrowid,
            f"{type_intervention} - {produit}",
            cursor,
        )
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

    def get_previsionnel_reel(self):
        import reporting

        return reporting.build_previsionnel_reel(self)

    def get_alertes_operationnelles(self, date_reference=None):
        import alerts

        return alerts.build_alertes_operationnelles(self, date_reference)

    def close(self):
        self.conn.close()
