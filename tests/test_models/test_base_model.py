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

    def test_kwargs_with_custom_attributes(self):
        """ Test creating instance with custom attributes """
        custom_attrs = {'name': 'test_name', 'value': 42}
        new = self.value(**custom_attrs)
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
