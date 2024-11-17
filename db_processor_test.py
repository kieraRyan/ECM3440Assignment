import unittest
import sqlite3
from unittest.mock import MagicMock, patch
import db_processor
import pytest

# Mock implementations for the helper functions
def mock_calculate_next_scene_name(movie_name):
    return f"{movie_name}_1"

def mock_get_next_scene_num_for_movie (movie_id):
    return movie_id

class TestDBClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Set up a shared in memory SQLite database for all tests when the class is initialized"""
        cls.connection = sqlite3.connect(":memory:")
    
    @classmethod
    def tearDownClass(cls):
        """Tear down the shared in-memory SQLite database after all tests have run."""
        cls.connection.close()

    def test_get_connection(self):
        # Set up an in-memory SQLite database for testing
       return self.connection
    
    @pytest.mark.run(order=1)
    @patch('db_processor.get_connection')
    def test_create_tables(self, mock_get_connection):
        """Test create_tables functions creates correct database schema"""

        # Mock connection to use in memory database
        mock_connection = MagicMock(wraps=self.connection)
        mock_get_connection.return_value = mock_connection
        
        # Replace the `close` method with a duff class so that we dont close the connection/ lose the in memory db
        mock_connection.close = MagicMock()

        # Call real create_tables function
        db_processor.create_tables()

        # Verify that connection.close() was called
        mock_connection.close.assert_called_once()

        # Verify the tables exist
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [row[0] for row in tables]

        self.assertTrue(len(tables) == 3, "3 tables created")
        self.assertTrue(table_names.index("MOVIE") > -1, "MOVIE table created")
        self.assertTrue(table_names.index("SCENE") > -1, "SCENE table created")
        self.assertTrue(table_names.index("STILL") > -1, "STILL table created")

        # Verify the schema of each table
        expected_movie_schema = [
            (0, "id", "INTEGER", 0, None, 1),
            (1, "name", "TEXT", 1, None, 0),
            (2, "filePath", "TEXT", 0, None, 0),
        ]
        # retrieves the schema for each table
        cursor.execute("PRAGMA table_info('MOVIE');")
        self.assertEqual(cursor.fetchall(), expected_movie_schema, "Verify columns created correctly in MOVIE table")

        expected_scene_schema = [
            (0, "id", "INTEGER", 0, None, 1),
            (1, "name", "TEXT", 1, None, 0),
            (2, "movieId", "INTEGER", 1, None, 0),
            (3, "order", "INTEGER", 1, None, 0),
        ]
        cursor.execute("PRAGMA table_info('SCENE');")
        self.assertEqual(cursor.fetchall(), expected_scene_schema, "Verify columns created correctly in SCENE table")

        expected_still_schema = [
            (0, "id", "INTEGER", 0, None, 1),
            (1, "name", "TEXT", 1, None, 0),
            (2, "sceneId", "INTEGER", 1, None, 0),
            (3, "order", "INTEGER", 1, None, 0),
            (4, "filePath", "TEXT", 1, None, 0),
        ]
        cursor.execute("PRAGMA table_info('STILL');")
        self.assertEqual(cursor.fetchall(), expected_still_schema, "Verify columns created correctly in STILL table")


    # @patch('db_processor.get_connection', side_effect= test_get_connection)
    # @pytest.mark.run(order=2)
    # @patch('db_processor.get_connection')
    # @patch('db_processor.calculate_next_scene_name', side_effect= mock_calculate_next_scene_name)
    # @patch('db_processor.get_next_scene_num_for_movie', side_effect= mock_get_next_scene_num_for_movie)
    # def test_create_new_scene(self, mock_get_connection, mock_calculate_next_scene_name, mock_get_next_scene_num_for_movie):
    #     print('testing scene creation')
    #     # Mock the connection object to use our in-memory database
    #     # mock_get_connection.return_value = self.connection

    #     mock_connection = MagicMock(wraps=self.connection)
    #     mock_get_connection.return_value = mock_connection
    #     # Replace the `close` method with a no-op
    #     mock_connection.close = MagicMock()



    #     # Mock cursor to return a specific value for the SELECT query
    #     # mock_cursor = MagicMock()
    #     # mock_connection.cursor.return_value = self.connection.cursor()
    #     # mock_cursor.fetchone.return_value = (1, "Movie_1_1", 1)  # Mock the result of the SELECT query

    #     # Inputs for the test
    #     movie_id = 1
    #     movie_name = "Movie_1"

    #     # Call the function to test
    #     result = db_processor.create_new_scene(movie_id, movie_name)
    #     print(type(result))

    # #     self.assertIsNotNone(result, "Return result should not be None")
    # #     print(result[1])
    # #    # self.assertEqual(result[1], "Movie_1_1", "Scene name should match the mock calculation")
    # #     self.assertEqual(result[2], 1, "Scene order should match the mock calculation")
        
    #     # Check if the record was actually inserted into the database
    #     cursor = self.connection.cursor()
    #     cursor.execute('SELECT id, name, "order" FROM SCENE WHERE id = ?', (result[0],))
    #     record = cursor.fetchone()

    #     self.assertIsNotNone(record, "Record should exist in the database")
    #     self.assertEqual(record[1], "Movie_1_1", "Inserted name should match")
    #     self.assertEqual(record[2], 1, "Inserted scene order should match")

    #     # check in error scenario by inputting incorrect type for movie_id integer value
    #     result = db_processor.create_new_scene("test value", "test value")
    #     self.assertEqual(result, (), "In an error scenario create_new_scene returns empty tuple")

if __name__ == '__main__':
    unittest.main()