#!/usr/bin/python3
""" """
from models.base_model import BaseModel
import unittest
import datetime
from uuid import UUID
import json
import os


class test_basemodel(unittest.TestCase):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        self.name = 'BaseModel'
        self.value = BaseModel

    def setUp(self):
        """ """
        pass

    def tearDown(self):
        try:
            os.remove('file.json')
        except Exception:
            pass

    def test_default(self):
        """ """
        i = self.value()
        self.assertEqual(type(i), self.value)

    def test_kwargs(self):
        """ """
        i = self.value()
        copy = i.to_dict()
        new = BaseModel(**copy)
        self.assertFalse(new is i)

    def test_kwargs_int(self):
        """ """
        i = self.value()
        copy = i.to_dict()
        copy.update({1: 2})
        with self.assertRaises(TypeError):
            new = BaseModel(**copy)

    def test_save(self):
        """ Testing save """
        i = self.value()
        i.save()
        key = self.name + "." + i.id
        with open('file.json', 'r') as f:
            j = json.load(f)
            self.assertEqual(j[key], i.to_dict())

    def test_str(self):
        """ """
        i = self.value()
        self.assertEqual(str(i), '[{}] ({}) {}'.format(self.name, i.id,
                         i.__dict__))

    def test_repr(self):
        """ Test __repr__ method """
        i = self.value()
        self.assertEqual(repr(i), str(i))
        self.assertEqual(repr(i), '[{}] ({}) {}'.format(self.name, i.id,
                         i.__dict__))

    def test_todict(self):
        """ """
        i = self.value()
        n = i.to_dict()
        self.assertEqual(i.to_dict(), n)

    def test_kwargs_none(self):
        """ """
        n = {None: None}
        with self.assertRaises(TypeError):
            new = self.value(**n)

    def test_kwargs_one(self):
        """ """
        n = {'Name': 'test'}
        # This should now work since we modified the BaseModel to handle any kwargs
        new = self.value(**n)
        self.assertEqual(new.Name, 'test')

    def test_id(self):
        """ """
        new = self.value()
        self.assertEqual(type(new.id), str)

    def test_created_at(self):
        """ """
        new = self.value()
        self.assertEqual(type(new.created_at), datetime.datetime)

    def test_updated_at(self):
        """ """
        new = self.value()
        self.assertEqual(type(new.updated_at), datetime.datetime)
        n = new.to_dict()
        new = BaseModel(**n)
        self.assertFalse(new.created_at == new.updated_at)

    def test_kwargs_with_custom_attributes(self):
        """ Test creating instance with custom attributes """
        custom_attrs = {'name': 'test_name', 'value': 42}
        new = self.value(**custom_attrs)
        self.assertEqual(new.name, 'test_name')
        self.assertEqual(new.value, 42)
        # Should still have timestamps
        self.assertTrue(hasattr(new, 'created_at'))
        self.assertTrue(hasattr(new, 'updated_at'))
        self.assertEqual(type(new.created_at), datetime.datetime)
        self.assertEqual(type(new.updated_at), datetime.datetime)

    def test_kwargs_without_timestamps(self):
        """ Test that timestamps are auto-added when not in kwargs """
        custom_attrs = {'name': 'test_name'}
        new = self.value(**custom_attrs)
        # Should automatically add timestamps
        self.assertTrue(hasattr(new, 'created_at'))
        self.assertTrue(hasattr(new, 'updated_at'))
        self.assertTrue(hasattr(new, 'id'))
        self.assertEqual(type(new.created_at), datetime.datetime)
        self.assertEqual(type(new.updated_at), datetime.datetime)

    def test_kwargs_with_explicit_timestamps(self):
        """ Test that explicit timestamps in kwargs are preserved """
        test_time = datetime.datetime(2022, 1, 1, 12, 0, 0)
        custom_attrs = {
            'name': 'test_name',
            'created_at': test_time.isoformat(),
            'updated_at': test_time.isoformat()
        }
        new = self.value(**custom_attrs)
        self.assertEqual(new.created_at, test_time)
        self.assertEqual(new.updated_at, test_time)

    def test_storage_new_called_with_kwargs(self):
        """ Test that storage.new is called even when using kwargs """
        from models import storage
        # Clear storage first to get accurate count
        storage._FileStorage__objects.clear()
        initial_count = len(storage.all())
        custom_attrs = {'name': 'test_name'}
        new = self.value(**custom_attrs)
        # Should be added to storage
        self.assertEqual(len(storage.all()), initial_count + 1)
        key = f"{self.name}.{new.id}"
        self.assertIn(key, storage.all())
