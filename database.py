import sqlite3
import pandas as pd

DB_FILE = "transferencias.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jugador TEXT NOT NULL,
            edad INTEGER,
            posicion TEXT,
            liga TEXT,
            club_origen TEXT,
            club_destino TEXT,
            valor REAL,
            tipo TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM transfers")
    count = cursor.fetchone()[0]
    
    if count == 0:
        initial_data = [
            ("Kylian Mbappé", 25, "Delantero", "La Liga", "Paris SG", "Real Madrid", 180.0, "Traspaso Libre"),
            ("Harry Kane", 30, "Delantero", "Bundesliga", "Tottenham", "Bayern Múnich", 95.0, "Traspaso Definitivo"),
            ("Declan Rice", 25, "Centrocampista", "Premier League", "West Ham", "Arsenal", 116.6, "Traspaso Definitivo"),
            ("Jude Bellingham", 20, "Centrocampista", "La Liga", "Borussia Dortmund", "Real Madrid", 103.0, "Traspaso Definitivo"),
            ("Moises Caicedo", 22, "Centrocampista", "Premier League", "Brighton", "Chelsea", 116.0, "Traspaso Definitivo"),
            ("Rasmus Højlund", 21, "Delantero", "Premier League", "Atalanta", "Manchester United", 73.9, "Traspaso Definitivo"),
            ("Kim Min-jae", 27, "Defensa", "Bundesliga", "Napoli", "Bayern Múnich", 50.0, "Traspaso Definitivo"),
            ("Benjamin Pavard", 28, "Defensa", "Serie A", "Bayern Múnich", "Inter de Milán", 30.0, "Traspaso Definitivo"),
            ("Ousmane Dembélé", 26, "Delantero", "Ligue 1", "Barcelona", "Paris SG", 50.0, "Traspaso Definitivo"),
            ("Sandro Tonali", 23, "Centrocampista", "Premier League", "AC Milan", "Newcastle United", 64.0, "Traspaso Definitivo"),
            ("Marcus Thuram", 26, "Delantero", "Serie A", "Borussia M'gladbach", "Inter de Milán", 0.0, "Traspaso Libre"),
            ("Randal Kolo Muani", 25, "Delantero", "Ligue 1", "Eintracht Frankfurt", "Paris SG", 95.0, "Traspaso Definitivo"),
            ("Josko Gvardiol", 22, "Defensa", "Premier League", "RB Leipzig", "Manchester City", 90.0, "Traspaso Definitivo"),
            ("Christian Pulisic", 25, "Delantero", "Serie A", "Chelsea", "AC Milan", 20.0, "Traspaso Definitivo"),
            ("João Félix", 24, "Delantero", "La Liga", "Atlético de Madrid", "FC Barcelona", 0.0, "Cesión")
        ]
        cursor.executemany("""
            INSERT INTO transfers (jugador, edad, posicion, liga, club_origen, club_destino, valor, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_data)
        conn.commit()
    conn.close()

def get_transfers_df():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT id, jugador as Jugador, edad as Edad, posicion as Posición, liga as Liga, club_origen as 'Club Origen', club_destino as 'Club Destino', valor as 'Valor (€M)', tipo as Tipo FROM transfers", conn)
    conn.close()
    return df

def add_transfer(jugador, edad, posicion, liga, club_origen, club_destino, valor, tipo):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transfers (jugador, edad, posicion, liga, club_origen, club_destino, valor, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (jugador, edad, posicion, liga, club_origen, club_destino, valor, tipo))
    conn.commit()
    conn.close()

def update_transfer(transfer_id, edad, posicion, liga, club_origen, club_destino, valor, tipo):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transfers 
        SET edad = ?, posicion = ?, liga = ?, club_origen = ?, club_destino = ?, valor = ?, tipo = ?
        WHERE id = ?
    """, (edad, posicion, liga, club_origen, club_destino, valor, tipo, transfer_id))
    conn.commit()
    conn.close()

def delete_transfer(transfer_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transfers WHERE id = ?", (transfer_id,))
    conn.commit()
    conn.close()
