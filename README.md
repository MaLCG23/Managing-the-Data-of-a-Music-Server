# Self-Hosted Music Library — Data Management Scripts

Scripts for managing the data of a self-hosted music server: adding new songs to the catalog and tagging/classifying them, synced with the server over SFTP.

📄 **[Full write-up here](./Managing_the_Data_of_a_Music_Server.pdf)** — covers the server/Docker/Liquidsoap setup, the design decisions behind each script, and what I learned along the way.

## Scripts

- **`create_db.py`** — Sets up the SQLite schema (songs, tags, and the song-tag link table). Run once on the server.
- **`add_songs.py`** — Scans a local folder for new audio files, extracts metadata, registers them in the database, and uploads everything to the server.
- **`categorize_songs.py`** — Interactive CLI for reviewing and tagging songs that are still unclassified.

## Setup

```
pip install paramiko tinytag prompt_toolkit
```

You'll also need a `datos_privados.py` file (not included) defining your server credentials:
```python
host = "your.server.ip"
usuario = "your_ssh_user"
contrasena = "your_ssh_password"
```
