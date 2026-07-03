import paramiko
import sqlite3
from tinytag import TinyTag
from datetime import date, timedelta
import datos_privados
import os

# Connection data
host = datos_privados.host #123.456.7.89 <- ip
user = datos_privados.usuario #Paco <-name_host 
pasword = datos_privados.contrasena # ***** <- server pasword

path_music_pc = "music_to_pass"
path_music_server = "mi_music"
path_db_pc = "temporal_music.db"
path_db_server = "music.db"

conn = None

try:
    #---- CONEXION WITH THE SERVER
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=pasword)
    sftp = ssh.open_sftp()

    #---- CONNECTION WITH DATABASE
    sftp.get(path_db_server, path_db_pc)
    conn = sqlite3.connect(path_db_pc)
    c = conn.cursor()

    #------ GET ALL THE FILES TO PASS
    files = [f for f in os.listdir(path_music_pc) if f.endswith((".mp3", ".flac", ".ogg"))]
    files_to_upload = []

    #------ BASIC INSERT STATEMENT
    SQL = """INSERT INTO SONGS (
            NAME, FILE_PATH, SIZE_MB, DURATION_MIN, REAL_DURATION,
            TITLE, ARTIST, ALBUM, GENRE, YEAR_SONG, BITRATE, 
            DATE_ADDED, COMMENT, CLASIFICATION
         ) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    
    #----- INSERT INTO DATABASE
    for file in files:
        song_name = os.path.splitext(file)[0]
        c.execute("SELECT NAME FROM SONGS WHERE NAME = ?", (song_name,))
        result = c.fetchone()
        if result is None:
            full_path_pc = os.path.join(path_music_pc, file)
            song = TinyTag.get(full_path_pc)

            file_path_server = path_music_server + "/" + file
            size_mb = song.filesize / (1024 * 1024)
            td = timedelta(seconds=song.duration)
            duration_min = str(td)[2:-3]
            today_date = date.today().isoformat()

            valores = (
                song_name,                  # NAME (the file name, e.g.: "song.mp3")
                file_path_server,           # FILE_PATH
                round(size_mb, 4),          # SIZE
                duration_min,               # DURATION IN MIN
                round(song.duration, 2),    # DURATION IN SEC
                song.title,                 # TITLE
                song.artist,                # ARTIST
                song.album,                 # ALBUM
                song.genre,                 # GENRE
                song.year,                  # YEAR_SONG
                round(song.bitrate, 2),     # BITRATE
                today_date,                 # DATE_ADDED
                song.comment,               # COMMENT
                0                           # IF CLASSIFICATION HAS BEEN COMPLETED OR NOT (0 BASE)
            )

            c.execute(SQL, valores)
            
            with open("ns.txt", "a") as f:
                f.write(full_path_pc + "\n")

            #-- SAVE THE FILE FROM PC TO SERVER
            files_to_upload.append((full_path_pc, file_path_server))

    #----- CLOSE IT ALL
    conn.commit()
    conn.close()
    
    #-- PASS THE FILE FROM PC TO SERVER AND DELETE
    sftp.put(path_db_pc, path_db_server)
    for path_pc, path_srv in files_to_upload:
        sftp.put(path_pc, path_srv)
        os.remove(path_pc)

        with open("ns.txt", "r") as f:
            lines = f.readlines()
        filtered_lines = [line for line in lines if line.strip("\n") != path_pc]  # <-- path_pc
        with open("ns.txt", "w") as f:
            f.writelines(filtered_lines)
                
    os.remove(path_db_pc)

    sftp.close()
    ssh.close()
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        conn.close()
    try:
        sftp.close()
        ssh.close()
    except:
        pass