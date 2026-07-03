import paramiko
import sqlite3
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import datos_privados
import os

def CLEAR():
    os.system('cls') #dev machine is Windows

# Connection data
host = datos_privados.host #123.456.7.89 <- ip
user = datos_privados.usuario #Paco <-name_host 
pasword = datos_privados.contrasena # ***** <- server pasword

path_db_server = "music.db"
path_db_pc = "temporal_music.db"

text_document_pc = "temporal_queue.txt"
text_document_server = "queue.txt"

conn = None
try:
    #---- CONEXION WITH THE SERVER
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=pasword)
    sftp = ssh.open_sftp()

    sftp.get(path_db_server, path_db_pc)
    conn = sqlite3.connect(path_db_pc)
    c = conn.cursor()

    #---- WHAT ARE YOU GOING TO CLASIFICATE
    try:
        print("DO YOU WANT TO CLASSIFY THE UNCLASSIFIED (0), STARTED (1), ALMOST CLASSIFIED (2):", end=" ")
        what_to_clasificate = int(input())

        print("\nDO YOU WANT TO FILTER BY DAY (N/Y):", end=" ")
        date = input()

        if date == "Y" or date =="y" or date == "S" or date == "s":
            print("\nENTER THE DATE AS YEAR-MONTH-DAY")
            date = input()
        else:
            date = None
    except:
        print("\nTHERE HAS BEEN AN ERROR. DEFAULT VALUES")
        what_to_clasificate = 0
        date = None

    c.execute("SELECT TAG_NAME FROM TAGS")
    all_tags_tuple = c.fetchall()
    tags_db = [tag for (tag,) in all_tags_tuple] + ["exit", "sup_exit", "create", "view"]
    completer_tags = WordCompleter(tags_db, ignore_case=True, match_middle=True)
    
    if date:
        c.execute("SELECT * FROM SONGS WHERE DATE_ADDED = ? AND CLASIFICATION = ? ORDER BY DATE_ADDED DESC", (date, what_to_clasificate))
    else:
        c.execute("SELECT * FROM SONGS WHERE CLASIFICATION = ? ORDER BY DATE_ADDED ASC", (what_to_clasificate,))

    lista = c.fetchall()
    force_close = False
    for i in lista:

        #-------- REPRODUCTION IN LIST
        song_to_reproduce = [i[2] + "\n"] * 10
        with open(text_document_pc, "w", newline="\n") as f:  # <-- newline="\n" NO /r WHICH IS THE DEFAULT IN WINDOWS (SERVER IN LINUX)
            f.writelines(song_to_reproduce)

        sftp.put(text_document_pc, text_document_server)

        comand = "python3 skips.py"
        stdin, stdout, stderr = ssh.exec_command(comand)
        exit_status = stdout.channel.recv_exit_status()  # blocks until it ends

        if exit_status != 0:
            error = stderr.read().decode()
            print(f"Server error: {error}")

        #------- CLASSIFICATION LOOP
        while True:
            c.execute("""SELECT T.TAG_NAME 
                      FROM TAGS AS T
                      JOIN SONGS_TAGS AS ST ON T.ID_TAG = ST.ID_TAG
                      WHERE ST.ID_SONG = ?""", (i[0],))
            current_tags_ugly = c.fetchall()
            current_tags = [ite for (ite,) in current_tags_ugly]

            CLEAR()
            print(f"NOW PUT THE TAGS THAT CORRESPOND TO THE SONG: {i[6]}")
            print(f"CURRENTLY IT HAS THE TAGS: ", end="")
            for k in current_tags:
                print(k, end=", ")
            print("\nWRITE THE NUMBERS OF THE TAGS, WRITE \"exit\" TO EXIT (\"sup_exit\" to exit completely), " \
            "WRITE \"create\" TO CREATE A NEW TAG, WRITE \"view\" TO SEE ALL TAGS: ")
            to_do = prompt("Enter action or TAG: ", completer=completer_tags).strip()

            if to_do == "exit":
                break

            elif to_do == "sup_exit":
                force_close = True
                break

            elif to_do == "view":
                CLEAR()
                for category in tags_db:
                    print(category, end=", ")
                print("\nNAME: ", end="")
                input()

            elif to_do == "create":
                CLEAR()
                print("ENTER THE NAME OF THE NEW CATEGORY: ", end="")
                name = input()
                print(f"\nARE YOU COMPLETELY SURE THAT {name} IS CORRECT (YES/NO): ", end="")
                verify = input()
                if verify in ["YES", "yes", "Yes", "Y", "y", "SI", "si", "Si"]:
                    c.execute("INSERT OR IGNORE INTO TAGS (TAG_NAME) VALUES (?)", (name,))
                    conn.commit()
                    c.execute("SELECT TAG_NAME FROM TAGS")
                    all_tags_tuple = c.fetchall()
                    tags_db = [tag for (tag,) in all_tags_tuple]  + ["exit", "sup_exit", "create", "view"]
                    completer_tags = WordCompleter(tags_db, ignore_case=True, match_middle=True)

            else:
                c.execute("SELECT ID_TAG FROM TAGS WHERE TAG_NAME = ?", (to_do,))
                response = c.fetchone()
                if response:
                    id_tag = response[0]
                    id_song = i[0]
                    c.execute("INSERT OR IGNORE INTO SONGS_TAGS (ID_SONG, ID_TAG) VALUES (?, ?)", (id_song, id_tag))
        
        while True:
            print("AT WHAT LEVEL IS THE SONG CLASSIFIED?")
            print("0 NO, 1 PARTIAL, 2 COMPLETE, 3 DO NOT TOUCH")
            try:
                is_classified = int(input())
            except:
                is_classified = 0
            
            if is_classified in [0, 1, 2, 3]:
                c.execute("UPDATE SONGS SET CLASIFICATION = ? WHERE ID_SONG = ?", (is_classified, i[0]))
                break

        conn.commit()
        if force_close:
            break
    
    with open(text_document_pc, "w", newline="\n") as f: #CLEAR QUEUE
        f.write("")

    sftp.put(text_document_pc, text_document_server)

    #---- CLOSE CONNECTIONS AND UPDATE DB
    conn.close()
    conn = None
    sftp.put(path_db_pc, path_db_server)
    sftp.close()
    ssh.close()
    os.remove(path_db_pc)
    
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