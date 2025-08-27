#!/usr/bin/python3
""" Test cases for console.py """
import unittest
import sys
import io
from contextlib import redirect_stdout
from console import HBNBCommand
from models import storage
from models.base_model import BaseModel
from models.state import State
from models.place import Place
import os


class TestConsole(unittest.TestCase):
    """ Test class for console functionality """

    def setUp(self):
        """ Set up test environment """
        self.console = HBNBCommand()

    def tearDown(self):
        """ Clean up after tests """
        try:
            os.remove('file.json')
        except Exception:
            pass

    def create_session(self, server=None):
        """ Create a test session """
        self.console = HBNBCommand()

    def test_create_with_parameters(self):
        """ Test create command with parameters """
        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('create State name="California"')
        output = f.getvalue().strip()
        # Should output just the ID
        self.assertTrue(len(output) == 36)  # UUID length
        
        # Check that object was created with correct attributes
        objects = storage.all()
        found = False
        for obj in objects.values():
            if hasattr(obj, 'name') and obj.name == 'California':
                found = True
                break
        self.assertTrue(found)

    def test_create_with_multiple_parameters(self):
        """ Test create command with multiple parameters """
        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('create Place city_id="0001" user_id="0001" '
                               'name="My_little_house" number_rooms=4 '
                               'number_bathrooms=2 max_guest=10 '
                               'price_by_night=300 latitude=37.773972 '
                               'longitude=-122.431297')
        output = f.getvalue().strip()
        # Should output just the ID
        self.assertTrue(len(output) == 36)  # UUID length
        
        # Check that object was created with correct attributes
        objects = storage.all()
        found = False
        for obj in objects.values():
            if (hasattr(obj, 'name') and obj.name == 'My little house' and
                hasattr(obj, 'number_rooms') and obj.number_rooms == 4 and
                hasattr(obj, 'latitude') and obj.latitude == 37.773972):
                found = True
                break
        self.assertTrue(found)

    def test_handle_params_string(self):
        """ Test parameter handling for strings """
        params = ['name="California"']
        result = self.console._HBNBCommand__handle_params(params)
        self.assertEqual(result['name'], 'California')

    def test_handle_params_string_with_underscore(self):
        """ Test parameter handling for strings with underscores """
        params = ['name="My_little_house"']
        result = self.console._HBNBCommand__handle_params(params)
        self.assertEqual(result['name'], 'My little house')

    def test_handle_params_integer(self):
        """ Test parameter handling for integers """
        params = ['number_rooms=4']
        result = self.console._HBNBCommand__handle_params(params)
        self.assertEqual(result['number_rooms'], 4)
        self.assertEqual(type(result['number_rooms']), int)

    def test_handle_params_float(self):
        """ Test parameter handling for floats """
        params = ['latitude=37.773972']
        result = self.console._HBNBCommand__handle_params(params)
        self.assertEqual(result['latitude'], 37.773972)
        self.assertEqual(type(result['latitude']), float)

    def test_handle_params_mixed(self):
        """ Test parameter handling for mixed types """
        params = ['name="Test_Place"', 'rooms=5', 'price=99.99']
        result = self.console._HBNBCommand__handle_params(params)
        self.assertEqual(result['name'], 'Test Place')
        self.assertEqual(result['rooms'], 5)
        self.assertEqual(result['price'], 99.99)

    def test_all_command_output_format(self):
        """ Test that all command outputs objects in correct format """
        # Create a test object first
        state = State(name="TestState")
        storage.new(state)
        storage.save()

        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('all State')
        output = f.getvalue().strip()
        
        # Output should be a list containing object representations
        self.assertTrue(output.startswith('['))
        self.assertTrue(output.endswith(']'))
        self.assertIn('[State]', output)
        self.assertIn(state.id, output)
        self.assertIn('created_at', output)
        self.assertIn('updated_at', output)
        self.assertIn('datetime.datetime', output)

    def test_create_missing_class(self):
        """ Test create command with missing class name """
        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('create')
        output = f.getvalue().strip()
        self.assertEqual(output, "** class name missing **")

    def test_create_invalid_class(self):
        """ Test create command with invalid class name """
        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('create InvalidClass')
        output = f.getvalue().strip()
        self.assertEqual(output, "** class doesn't exist **")

    def test_created_objects_have_timestamps(self):
        """ Test that created objects have proper timestamps """
        with redirect_stdout(io.StringIO()) as f:
            self.console.onecmd('create State name="TestState"')
        output = f.getvalue().strip()
        
        # Find the created object
        objects = storage.all()
        created_obj = None
        for obj in objects.values():
            if obj.id == output:
                created_obj = obj
                break
        
        self.assertIsNotNone(created_obj)
        self.assertTrue(hasattr(created_obj, 'created_at'))
        self.assertTrue(hasattr(created_obj, 'updated_at'))
        import datetime
        self.assertEqual(type(created_obj.created_at), datetime.datetime)
        self.assertEqual(type(created_obj.updated_at), datetime.datetime)


if __name__ == '__main__':
    unittest.main()
