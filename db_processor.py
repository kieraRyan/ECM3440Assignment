import sqlite3
import csv
import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def create_tables() -> bool:
        """
        Creates the Order, Item and OrderItem tables within the database.
        Returns True/ False to indicate the success of the above.
        """
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('DROP TABLE IF EXISTS MOVIE;')
            cursor.execute('CREATE TABLE IF NOT EXISTS "MOVIE"' +
                                  '(id INTEGER PRIMARY KEY,name TEXT NOT NULL, filePath TEXT);')	
            
            cursor.execute('DROP TABLE IF EXISTS SCENE;')
            cursor.execute('CREATE TABLE IF NOT EXISTS "SCENE"' +
                            '(id INTEGER PRIMARY KEY,name TEXT NOT NULL, movieId INTEGER NOT NULL, "order" INTEGER NOT NULL, FOREIGN KEY (movieId) REFERENCES MOVIE (id) ON DELETE CASCADE ON UPDATE NO ACTION);')
            
            cursor.execute('DROP TABLE IF EXISTS STILL;')
            cursor.execute('CREATE TABLE IF NOT EXISTS "STILL"' +
                            '(id INTEGER PRIMARY KEY,name TEXT NOT NULL, sceneId INTEGER NOT NULL, "order" INTEGER NOT NULL, filePath TEXT NOT NULL, FOREIGN KEY (sceneId) REFERENCES SCENE (id) ON DELETE CASCADE ON UPDATE NO ACTION);')
           
            # Commit the changes to the database
            connection.commit()
            connection.close()
        except sqlite3.OperationalError as e:
            connection.rollback()
            connection.close()

def print_all_tables():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())
        connection.close()

    except sqlite3.OperationalError as e:
        print(e)
        connection.rollback()
        connection.close()
    
def get_all_movies() -> object:
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, name, filePath FROM MOVIE')

    records = cursor.fetchall()    
    connection.close()
    return records

def get_scenes_for_movie(movie_id: int) -> object:
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, name, "order" FROM SCENE WHERE movieId = ?', (str(movie_id),))
    records = cursor.fetchall()
    
    connection.close()
    return records

def get_stills_for_scene(scene_id: int) -> object:
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT id, name, sceneId, "order", filePath FROM STILL WHERE sceneId = ?', (str(scene_id),))
    records = cursor.fetchall()

    connection.close()
    return records

def calculate_next_movie_name () -> str:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute("SELECT id FROM MOVIE ORDER BY id DESC")
    all_movies = cursor.fetchall();

    if len(all_movies) < 1:
        name = 'Movie_1'
    else:
        name = 'Movie_' + str(all_movies[0][0] + 1)

    connection.commit()
    connection.close()
    # return id of inserted movie
    return name

def create_new_movie () -> list:
    
    connection = get_connection()
    cursor = connection.cursor()

    new_name = calculate_next_movie_name()
            
    cursor.execute("INSERT INTO MOVIE (name) VALUES (?);", (new_name,))
    connection.commit()
    connection.close()
    # return id of inserted movie
    return [cursor.lastrowid, new_name]

def calculate_next_still_name (scene_name) -> str:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute('SELECT id FROM "STILL" ORDER BY id DESC')
    all_stills = cursor.fetchall();

    if len(all_stills) < 1:
        name = scene_name + '_1' + '.png'
    else:
        name = scene_name + '_' + str(all_stills[0][0] + 1) + '.png'

    connection.commit()
    connection.close()
    return name

def get_next_still_num_for_scene (scene_id: int) -> int:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute('SELECT "order" FROM "STILL" WHERE sceneId = ? ORDER BY id DESC', (scene_id, ))
    stills_in_scene = cursor.fetchall();

    if len(stills_in_scene) < 1:
        order = 1
    else:
        order = stills_in_scene[0][0] + 1

    connection.commit()
    connection.close()
    return order

def create_new_still (still_name, scene_id, path) -> int:
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('INSERT INTO STILL (name, sceneId, "order", filePath) VALUES (?, ?, ?, ?);', (still_name, scene_id, get_next_still_num_for_scene(scene_id), path))
    connection.commit()
    connection.close()
    # return id of inserted movie
    return cursor.lastrowid

def calculate_next_scene_name (movie_name) -> str:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute('SELECT id FROM "SCENE" ORDER BY id DESC')
    all_stills = cursor.fetchall();

    if len(all_stills) < 1:
        name = movie_name + '_1'
    else:
        name = movie_name + '_' + str(all_stills[0][0] + 1)

    connection.commit()
    connection.close()
    return name

def get_next_scene_num_for_movie (movie_id) -> int:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute('SELECT "order" FROM "SCENE" WHERE movieId = ? ORDER BY id DESC', (movie_id, ))
    scenes_in_movie = cursor.fetchall();

    if len(scenes_in_movie) < 1:
        order = 1
    else:
        order = scenes_in_movie[0][0] + 1

    connection.commit()
    connection.close()
    return order

def create_new_scene (movie_id: int, movie_name: str) -> tuple:
    """
    Creates new record in the SCENE table referncing the input movie ID 
    Returns the created record in a tuple format if success and an empty tuple if not successful
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute('INSERT INTO SCENE (name, movieId, "order") VALUES (?, ?, ?);', (calculate_next_scene_name(movie_name), movie_id, get_next_scene_num_for_movie(movie_id)))
        connection.commit()

        cursor.execute('SELECT id, name, "order" FROM SCENE WHERE id= ?', (int(cursor.lastrowid), ))
        insert_record = cursor.fetchone()
        connection.close()

        return insert_record
    except sqlite3.OperationalError as e:
        connection.rollback()
        connection.close()
        return ()

def delete_still (still_id: int) -> bool:
    try:
        connection = get_connection()
        cursor = connection.cursor()
        # first delete all related stills
        cursor.execute('DELETE FROM STILL WHERE id = ?;', (int(still_id), ))
        connection.commit()

        connection.close()
        return True
    except sqlite3.OperationalError as e:
        connection.rollback()
        connection.close()
        return False
    
def delete_scene (scene_id: int) -> bool:
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute('DELETE FROM SCENE WHERE id= ?;', (int(scene_id), ))
        connection.commit()

        connection.close()
        return True
    except sqlite3.OperationalError as e:
        connection.rollback()
        connection.close()
        return False

def get_connection():
    cnn = sqlite3.connect('movie_application_db.sqlite3')
    return cnn

def get_all_stills () -> object:
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT * from STILL')
    records = cursor.fetchall()

    connection.close()
    return records

def get_stills_for_movie (movie_id: int) -> object:
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT STILL.id, STILL.name, SCENE.id AS scene_id, STILL."order", STILL.filePath FROM STILL LEFT JOIN SCENE ON SCENE.id = STILL.sceneId LEFT JOIN MOVIE ON MOVIE.id = SCENE.movieId WHERE MOVIE.id = ?', (str(movie_id),))
    records = cursor.fetchall()

    connection.close()
    return records

def get_movie_stills_in_order (movie_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    results = []
    
    cursor.execute('SELECT id FROM SCENE WHERE movieId = ? ORDER BY "ORDER" ASC;', (str(movie_id),))
    scenes = cursor.fetchall()

    for id in scenes:
        results += cursor.execute('SELECT filePath FROM STILL WHERE sceneId = ? ORDER BY "ORDER" ASC;', (str(id[0]),)).fetchall()

    connection.close()
    return results

# create_tables()