import sqlite3
import csv
import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def create_tables() -> bool:
        """Creates the Order, Item and OrderItem tables within the database.
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
            print(e)
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
    answer_obj = [{
        'id': i[0],
        'name': i[1],
        'sceneId': i[2],
        'order': i[3],
        'filePath': i[4]
        } for i in records]
    connection.close()
    return answer_obj

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

def create_new_still (still_name, scene_id, order, path) -> int:
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('INSERT INTO STILL (name, sceneId, "order", filePath) VALUES (?, ?, ?, ?);', (still_name, scene_id, order, path))
    connection.commit()
    connection.close()
    # return id of inserted movie
    return cursor.lastrowid

def calculate_next_scene_name (movie_name, movie_id) -> str:
    connection = get_connection()
    cursor = connection.cursor()
            
    cursor.execute('SELECT id FROM "SCENE"  WHERE movieId = ? ORDER BY id DESC', (movie_id, ))
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

def create_new_scene (movie_id, movie_name) -> list:
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('INSERT INTO SCENE (name, movieId, "order") VALUES (?, ?, ?);', (calculate_next_scene_name(movie_name, movie_id), movie_id, get_next_scene_num_for_movie(movie_id)))
    connection.commit()

    cursor.execute('SELECT id, name, "order" FROM SCENE WHERE id= ?', (int(cursor.lastrowid), ))
    insert_record = cursor.fetchone()
    connection.close()

    return insert_record

def get_connection():
    cnn = sqlite3.connect('movie_application_db.sqlite3')
    return cnn

# create_tables()



def get_all_survey_data_for_airline(airline_id):
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT SURVEY.id, SURVEY.name, active, AIRLINE.name' +
                                      ' FROM SURVEY ' +
                                      'INNER JOIN AIRLINE on AIRLINE.id = ' +
                                      'SURVEY.airlineID WHERE SURVEY.airlineID = ' + str(airline_id))
    records = cursor.fetchall()
    answer_obj = [{
        'id': i[0],
        'name': i[1],
        'active': i[2],
        'airline': i[3]
        } for i in records]
    connection.close()
    return answer_obj

def get_all_survey_locations ():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT surveyID, locationID FROM SURVEYLOCATION')
    records = cursor.fetchall()
    answer_obj = [{
        'SurveyID': i[0],
        'LocationID': i[1]
        } for i in records]
    connection.close()
    return answer_obj

def get_all_questions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT QUESTION.id, Question.typeID, QUESTION.string, QUESTION.surveyID, QUESTION.range, QUESTION.active, QUESTION.choiceTypeID' +
                                      ' FROM QUESTION')
    records = cursor.fetchall()
    answer_obj = [
        {"ID": i[0], 
            "TypeID": i[1], 
            "String": i[2], 
            "SurveyID": i[3], 
            "Range": i[4], 
            "Active": i[5], 
            "ChoiceTypeID": i[6]
        } for i in records]
    connection.close()
    return answer_obj

# RETURN QUESTIONS IN THE GIVEN FORMAT WHERE SURVEYID = THE INPUT SURVEY ID
def get_questions(survey_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT QUESTION.id, QUESTIONTYPE.type, QUESTION.string, QUESTION.active' +
                                      ' FROM QUESTION ' +
                                      'INNER JOIN QUESTIONTYPE on QUESTIONTYPE.id = ' +
                                      'QUESTION.typeID WHERE surveyID = ' + str(survey_id))
    records = cursor.fetchall()
    answer_obj = [{
        'id': i[0],
        'type': i[1],
        'text': i[2],
        'active': i[3]
        } for i in records]
    connection.close()
    return answer_obj
    
# RETURN LOCATIONS IN THE GIVEN FORMAT BY QUERYING SURVEYLOCATION TABLE AND FINDING ALL LOCATIONS WHERE SURVEYID = THE INPUT SURVEY ID
def get_location_by_survey(survey_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT LOCATION.id, LOCATION.name' +
                                      ' FROM SURVEYLOCATION ' +
                                      'INNER JOIN LOCATION on LOCATION.id = ' +
                                      'SURVEYLOCATION.locationID WHERE surveyID = ' + str(survey_id))
    records = cursor.fetchall()
    connection.close()
    answer_obj = [{
        'id': i[0],
        'name': i[1]
        } for i in records]
    return answer_obj

def get_question_choices():
    return True

def get_all_question_choices():
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('SELECT questionID, choiceID, CHOICE.choiceText FROM QUESTIONCHOICE INNER JOIN CHOICE on CHOICE.id = QUESTIONCHOICE.choiceID')
    records = cursor.fetchall()
    answer_obj = [{
        'QuestionID': i[0],
        'ChoiceIDNum': i[1],
        'ChoiceID': i[2]
        } for i in records]
    connection.close()
    return answer_obj

def get_all_question_types():
    return {'field': 'val'}

def validate_login_details(user_name, pwd):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT username, accessLevel, AIRLINE.id' +
                                      ' FROM USER INNER JOIN AIRLINE ON AIRLINE.id = USER.airlineID' +
                                      ' WHERE username = ? AND password = ? ', (str(user_name), str(pwd)))
    records = cursor.fetchone()
    
    # if no records returned, invalid validation
    if records == None:
        return False
    
    answer_obj = {
        'user_name': records[0],
        'access_level': records[1],
        'airline_id': records[2]
        
        }
    connection.close()
    return answer_obj

def register_new_user(username, password, name, surname, access, email ):
    # registration was successful
    return True

def new_survey_response (body):
    # Each Q is an object containing ID and response for specific question
    # survey creation was successful was successful
    return True

def smiley_face_response (id, answer):
# this will be the response to the smiley face question
# could give this a location as well ? 
    return True

def get_locations ():
    # get the list of locations to send to the UI 
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT LOCATION.name FROM LOCATION')
    records = cursor.fetchall()
    connection.close()
    
    answer_obj = {'locations': [i[0] for i in records]}
    return answer_obj

def map_question_choices(choices, all_choices):
    # not a choice question
    if choices == 'NULL':
        return ''
    original_list = choices.split(',')
    translated_list = []
    for c in original_list:
        for choice in all_choices:
            if str(choice["ChoiceIDNum"]) == str(c):
                translated_list.append(choice['ChoiceID'])
                break

    # single choice option
    if len(translated_list) == 1:
        return translated_list[0]
    
    return ",".join(translated_list)
    

def get_all_answers():
    connection = get_connection()
    cursor = connection.cursor()

    choices = get_all_question_choices()
    
    cursor.execute('SELECT ANSWER.id, questionID, answerString, choiceID, locationID, date FROM ANSWER')
    records = cursor.fetchall()

    answer_obj = [{
        'ID': i[0],
        'QuestionID': i[1],
        'AnswerString': i[2],
        'ChoiceID': map_question_choices(i[3], choices),
        'LocationID': i[4],
        'Date': i[5]
        } for i in records]
    
    connection.close()
    return answer_obj

