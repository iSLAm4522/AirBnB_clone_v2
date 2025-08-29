#!/usr/bin/python3
""" Module for testing database storage"""
import unittest
import os
from os import getenv
import MySQLdb
from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review
from models import storage


@unittest.skipIf(getenv("HBNB_TYPE_STORAGE") != "db", "DBStorage tests only for db storage")
class TestDBStorage(unittest.TestCase):
    """Test cases for the database storage engine"""

    @classmethod
    def setUpClass(cls):
        """Set up the class before any tests"""
        if getenv("HBNB_TYPE_STORAGE") != "db":
            print("\nSkipping DBStorage tests (HBNB_TYPE_STORAGE != db)")
            return
        
        print("\nRunning DBStorage tests...")

    def setUp(self):
        """Set up test environment"""
        if getenv("HBNB_TYPE_STORAGE") != "db":
            self.skipTest("DBStorage tests only work with db storage")
        
        # Save existing environment variables to restore later
        self.hbnb_env = getenv("HBNB_ENV", "")
        self.hbnb_mysql_user = getenv("HBNB_MYSQL_USER", "")
        self.hbnb_mysql_pwd = getenv("HBNB_MYSQL_PWD", "")
        self.hbnb_mysql_host = getenv("HBNB_MYSQL_HOST", "")
        self.hbnb_mysql_db = getenv("HBNB_MYSQL_DB", "")
        
        # Set test environment variables
        os.environ["HBNB_ENV"] = "test"
        os.environ["HBNB_MYSQL_USER"] = getenv("HBNB_MYSQL_USER", "hbnb_test")
        os.environ["HBNB_MYSQL_PWD"] = getenv("HBNB_MYSQL_PWD", "hbnb_test_pwd")
        os.environ["HBNB_MYSQL_HOST"] = getenv("HBNB_MYSQL_HOST", "localhost") 
        os.environ["HBNB_MYSQL_DB"] = getenv("HBNB_MYSQL_DB", "hbnb_test_db")
        
        # Create a database connection for direct database operations
        # (not using SQLAlchemy)
        try:
            self.conn = MySQLdb.connect(
                host=os.environ["HBNB_MYSQL_HOST"],
                user=os.environ["HBNB_MYSQL_USER"],
                passwd=os.environ["HBNB_MYSQL_PWD"],
                db=os.environ["HBNB_MYSQL_DB"]
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            self.skipTest(f"Cannot connect to MySQL: {e}")

    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
        # Restore original environment variables
        if self.hbnb_env:
            os.environ["HBNB_ENV"] = self.hbnb_env
        else:
            os.environ.pop("HBNB_ENV", None)
            
        if self.hbnb_mysql_user:
            os.environ["HBNB_MYSQL_USER"] = self.hbnb_mysql_user
        else:
            os.environ.pop("HBNB_MYSQL_USER", None)
            
        if self.hbnb_mysql_pwd:
            os.environ["HBNB_MYSQL_PWD"] = self.hbnb_mysql_pwd
        else:
            os.environ.pop("HBNB_MYSQL_PWD", None)
            
        if self.hbnb_mysql_host:
            os.environ["HBNB_MYSQL_HOST"] = self.hbnb_mysql_host
        else:
            os.environ.pop("HBNB_MYSQL_HOST", None)
            
        if self.hbnb_mysql_db:
            os.environ["HBNB_MYSQL_DB"] = self.hbnb_mysql_db
        else:
            os.environ.pop("HBNB_MYSQL_DB", None)

    def test_all_method(self):
        """Test that all method returns a dictionary"""
        result = storage.all()
        self.assertIsInstance(result, dict)
    
    def test_all_with_class(self):
        """Test all method with a specific class"""
        # Create a state
        state = State(name="Test State")
        storage.new(state)
        storage.save()
        
        # Get all states
        result = storage.all(State)
        
        # There should be at least one state
        self.assertGreater(len(result), 0)
        
        # All results should be State objects
        for obj in result.values():
            self.assertIsInstance(obj, State)
        
        # Delete the test state
        storage.delete(state)
        storage.save()
    
    def test_new_method(self):
        """Test that new adds an object to the database"""
        # Get initial count of states
        self.cursor.execute("SELECT COUNT(*) FROM states")
        initial_count = self.cursor.fetchone()[0]
        
        # Create new state
        state = State(name="Test New State")
        storage.new(state)
        storage.save()
        
        # Get updated count of states
        self.cursor.execute("SELECT COUNT(*) FROM states")
        updated_count = self.cursor.fetchone()[0]
        
        # There should be one more state
        self.assertEqual(updated_count, initial_count + 1)
        
        # Delete the test state
        storage.delete(state)
        storage.save()
    
    def test_save_method(self):
        """Test that save actually saves to the database"""
        # Get initial count of states
        self.cursor.execute("SELECT COUNT(*) FROM states")
        initial_count = self.cursor.fetchone()[0]
        
        # Create a state but don't call save yet
        state = State(name="Test Save State")
        storage.new(state)
        
        # Count should still be the same
        self.cursor.execute("SELECT COUNT(*) FROM states")
        count_before_save = self.cursor.fetchone()[0]
        self.assertEqual(count_before_save, initial_count)
        
        # Now save
        storage.save()
        
        # Count should be increased by 1
        self.cursor.execute("SELECT COUNT(*) FROM states")
        count_after_save = self.cursor.fetchone()[0]
        self.assertEqual(count_after_save, initial_count + 1)
        
        # Delete the test state
        storage.delete(state)
        storage.save()
    
    def test_delete_method(self):
        """Test that delete removes an object from the database"""
        # Create a state
        state = State(name="Test Delete State")
        storage.new(state)
        storage.save()
        
        # Get count of states
        self.cursor.execute("SELECT COUNT(*) FROM states")
        count_before_delete = self.cursor.fetchone()[0]
        
        # Delete the state
        storage.delete(state)
        storage.save()
        
        # Count should be decreased by 1
        self.cursor.execute("SELECT COUNT(*) FROM states")
        count_after_delete = self.cursor.fetchone()[0]
        self.assertEqual(count_after_delete, count_before_delete - 1)
    
    def test_reload_method(self):
        """Test that reload works properly"""
        # Basic test - just make sure it doesn't throw an exception
        try:
            storage.reload()
        except Exception as e:
            self.fail(f"Reload raised exception: {e}")
        
        # Check if we can query objects after reload
        try:
            all_states = storage.all(State)
            # Just checking the result is a dict is sufficient
            self.assertIsInstance(all_states, dict)
        except Exception as e:
            self.fail(f"Failed to query objects after reload: {e}")
    
    def test_state_city_relationship(self):
        """Test that relationships between State and City work correctly"""
        # Create a state
        state = State(name="Test Relationship State")
        storage.new(state)
        storage.save()
        
        # Create a city in that state
        city = City(name="Test City", state_id=state.id)
        storage.new(city)
        storage.save()
        
        # Query city with SQL to check if it has the correct state_id
        self.cursor.execute(f"SELECT state_id FROM cities WHERE id='{city.id}'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], state.id)
        
        # Clean up
        storage.delete(city)
        storage.delete(state)
        storage.save()

    def test_object_persistence(self):
        """Test that objects persist across storage reloads"""
        # Create a state
        state = State(name="Persistence Test State")
        storage.new(state)
        storage.save()
        state_id = state.id
        
        # Now reload storage and see if we can find the state
        storage.reload()
        
        # Find our test state in the reloaded storage
        all_states = storage.all(State)
        found_state = None
        for obj_id, obj in all_states.items():
            if obj.id == state_id:
                found_state = obj
                break
        
        # Verify the state was found and has the correct attributes
        self.assertIsNotNone(found_state, "State not found after reload")
        if found_state is not None:
            self.assertEqual(found_state.name, "Persistence Test State")
        
        # Clean up
        if found_state is not None:
            storage.delete(found_state)
        else:
            storage.delete(state)
        storage.save()

    def test_storage_object_count(self):
        """Test that objects are properly counted"""
        # Get initial count
        initial_count = len(storage.all())
        
        # Create a state
        state = State(name="Test Count State")
        storage.new(state)
        storage.save()
        
        # Count should be increased
        new_count = len(storage.all())
        self.assertGreater(new_count, initial_count)
        
        # Clean up
        storage.delete(state)
        storage.save()

    def test_user_creation(self):
        """Test creation of User objects"""
        # Get initial count of users
        self.cursor.execute("SELECT COUNT(*) FROM users")
        initial_count = self.cursor.fetchone()[0]
        
        # Create a user
        user = User(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        storage.new(user)
        storage.save()
        
        # Get updated count of users
        self.cursor.execute("SELECT COUNT(*) FROM users")
        updated_count = self.cursor.fetchone()[0]
        
        # There should be one more user
        self.assertEqual(updated_count, initial_count + 1)
        
        # Check if the user was saved with correct values
        self.cursor.execute(
            f"SELECT email, password, first_name, last_name FROM users WHERE id='{user.id}'"
        )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "test@example.com")
        self.assertEqual(result[2], "Test")
        self.assertEqual(result[3], "User")
        
        # Clean up
        storage.delete(user)
        storage.save()

    def test_review_relationships(self):
        """Test the relationships for Review objects"""
        # Create state, city, user, place first
        state = State(name="Review Test State")
        storage.new(state)
        
        city = City(name="Review Test City", state_id=state.id)
        storage.new(city)
        
        user = User(
            email="reviewer@example.com",
            password="password123",
            first_name="Test",
            last_name="Reviewer"
        )
        storage.new(user)
        
        place = Place(
            name="Review Test Place",
            city_id=city.id,
            user_id=user.id,
            description="A place to review",
            number_rooms=1,
            number_bathrooms=1,
            max_guest=2,
            price_by_night=100
        )
        storage.new(place)
        storage.save()
        
        # Create a review
        review = Review(
            text="This is a great place!",
            place_id=place.id,
            user_id=user.id
        )
        storage.new(review)
        storage.save()
        
        # Check that the review was saved with the correct relationships
        self.cursor.execute(
            f"SELECT place_id, user_id FROM reviews WHERE id='{review.id}'"
        )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], place.id)
        self.assertEqual(result[1], user.id)
        
        # Clean up
        storage.delete(review)
        storage.delete(place)
        storage.delete(user)
        storage.delete(city)
        storage.delete(state)
        storage.save()

    def test_invalid_foreign_key(self):
        """Test that objects with invalid foreign keys cannot be saved"""
        # Try to create a city with non-existent state_id
        city = City(name="Invalid City", state_id="nonexistent_id")
        storage.new(city)
        
        # Attempting to save should raise an exception
        with self.assertRaises(Exception):
            storage.save()
            
        # Clean up any potential partial saves
        try:
            storage.delete(city)
            storage.save()
        except:
            pass

    def test_missing_required_fields(self):
        """Test that objects cannot be saved without required fields"""
        # Try to create a user without required email
        user = User(password="test123", first_name="Test", last_name="User")
        storage.new(user)
        
        # Attempting to save should raise an exception
        with self.assertRaises(Exception):
            storage.save()
            
        # Clean up any potential partial saves
        try:
            storage.delete(user)
            storage.save()
        except:
            pass

    def test_delete_nonexistent_object(self):
        """Test deleting an object that doesn't exist in storage"""
        # Create a state object but don't save it
        state = State(name="Nonexistent State")
        
        # Deleting an unsaved object should not raise an exception
        try:
            storage.delete(state)
            storage.save()
        except Exception as e:
            self.fail(f"Deleting nonexistent object raised: {e}")

    def test_multiple_object_operations(self):
        """Test handling multiple object operations in one transaction"""
        # Create multiple objects
        objects = [
            State(name=f"Test State {i}") for i in range(5)
        ]
        
        # Get initial count
        self.cursor.execute("SELECT COUNT(*) FROM states")
        initial_count = self.cursor.fetchone()[0]
        
        # Add all objects
        for obj in objects:
            storage.new(obj)
        storage.save()
        
        # Verify all objects were saved
        self.cursor.execute("SELECT COUNT(*) FROM states")
        after_save_count = self.cursor.fetchone()[0]
        self.assertEqual(after_save_count, initial_count + 5)
        
        # Delete all objects
        for obj in objects:
            storage.delete(obj)
        storage.save()
        
        # Verify all objects were deleted
        self.cursor.execute("SELECT COUNT(*) FROM states")
        final_count = self.cursor.fetchone()[0]
        self.assertEqual(final_count, initial_count)

    def test_user_email_validation(self):
        """Test that user email validation works"""
        # Try to create a user with invalid email
        user = User(
            email="invalid_email",  # Invalid email format
            password="password123",
            first_name="Test",
            last_name="User"
        )
        storage.new(user)
        
        # Attempting to save should raise an exception
        with self.assertRaises(Exception):
            storage.save()
            
        # Clean up any potential partial saves
        try:
            storage.delete(user)
            storage.save()
        except:
            pass

    def test_place_numeric_constraints(self):
        """Test numeric constraints for Place attributes"""
        # Create required related objects first
        state = State(name="Test State")
        storage.new(state)
        
        city = City(name="Test City", state_id=state.id)
        storage.new(city)
        
        user = User(
            email="test@test.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        storage.new(user)
        storage.save()
        
        # Try to create a place with invalid numeric values
        place = Place(
            name="Test Place",
            city_id=city.id,
            user_id=user.id,
            number_rooms=-1,  # Invalid negative value
            number_bathrooms=0,
            max_guest=-5,  # Invalid negative value
            price_by_night=-100  # Invalid negative value
        )
        storage.new(place)
        
        # Attempting to save should raise an exception
        with self.assertRaises(Exception):
            storage.save()
            
        # Clean up
        storage.delete(user)
        storage.delete(city)
        storage.delete(state)
        storage.save()
