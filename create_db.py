import sqlite3

conn = sqlite3.connect("music.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS "SONGS" (
    "ID_SONG"           INTEGER PRIMARY KEY,
    "NAME"              TEXT UNIQUE,
    "FILE_PATH"         TEXT,
    "SIZE_MB"           REAL,
    "DURATION_MIN"      TEXT,
    "REAL_DURATION"     REAL,
    "TITLE"             TEXT,
    "ARTIST"            TEXT,
    "ALBUM"             TEXT,
    "GENRE"             TEXT,
    "YEAR_SONG"         TEXT,
    "BITRATE"           REAL,
    "DATE_ADDED"        TEXT,
    "COMMENT"           TEXT,
    "CLASIFICATION"     INTEGER
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS "TAGS" (
    "ID_TAG"            INTEGER PRIMARY KEY,
    "TAG_NAME"          TEXT UNIQUE NOT NULL
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS "SONGS_TAGS" (
    "ID_SONG"       INTEGER,
    "ID_TAG"        INTEGER,
    PRIMARY KEY ("ID_SONG", "ID_TAG")
);
""")

conn.commit()
conn.close()


"""
valores = (
        song_name,                  # NAME (the file name, e.g.: "Dale_Zelda_Dale")
        file_path,                  # FILE_PATH
        round(size_mb, 4),          # SIZE
        duration_min,               # DURATION IN MIN
        round(song.duration, 2),    # DURATION IN SEC
        song.title,                 # TITLE (REAL TITLE)
        song.artist,                # ARTIST
        song.album,                 # ALBUM
        song.genre,                 # GENRE
        song.year,                  # YEAR_SONG
        round(song.bitrate, 2),     # BITRATE
        today_date,                 # DATE_ADDED <--- Fill manually (e.g.: current datetime)
        song.comment,               # COMMENT
        0                           # IF CLASSIFICATION HAS BEEN COMPLETED OR NOT (0 NO, 1 PARTIAL, 2 COMPLETE, 3 DO NOT TOUCH)
    )
"""