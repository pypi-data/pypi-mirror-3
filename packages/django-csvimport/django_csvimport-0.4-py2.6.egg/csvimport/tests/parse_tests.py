# -*- coding: utf-8 -*-
# Use unicode source code to make test character string writing easier
import os

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from csvimport.management.commands.csvimport import Command
from csvimport.tests.models import Country, UnitOfMeasure, Item, Organisation

class DummyFileObj:
    """ Use to replace html upload / or command arg 
        with test fixtures files 
    """
    path = ''

    def set_path(self, filename):
        self.path = os.path.join(os.path.dirname(__file__), 
                                 'fixtures',
                                 filename)

class CommandParseTest(TestCase):
    """ Run test of file parsing """

    def command(self, filename, defaults='country=KE(Country|code)'):
        """ Run core csvimport command to parse file """
        cmd = Command()
        uploaded = DummyFileObj()
        uploaded.set_path(filename)
        cmd.setup(mappings='', 
                  modelname='tests.Item', 
                  uploaded=uploaded,
                  defaults=defaults)

        # Report back any parse errors and fail test if they exist
        errors = cmd.run(logid='commandtest')
        error = errors.pop()
        self.assertEqual(error, 'Using mapping from first row of CSV file')
        if errors:
            for err in errors:
                print err
        self.assertEqual(errors, [])

    def get_item(self, code_share='sheeting'):
        """ Get item for confirming import is OK """
        try:
            item = Item.objects.get(code_share__exact=code_share)
        except ObjectDoesNotExist:
            item = None
        self.assertTrue(item, 'Failed to get row from imported test.csv Items')
        return item

    def test_plain(self, filename='test_plain.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.command(filename)
        item = self.get_item('sheeting')
        # Check a couple of the fields in Item    
        self.assertEqual(item.code_org, 'RF007')
        self.assertEqual(item.description, 'Plastic sheeting, 4*60m, roll')
        # Check related Organisation model is created
        self.assertEqual(item.organisation.name, 'Save UK')
        Item.objects.all().delete()

    def test_char(self, filename='test_char.csv'):
        """ Use custom command parse file - test with odd non-ascii character """
        self.command(filename)
        item = self.get_item('watercan')
        self.assertEqual(item.code_org, 'CWATCONT20F')
        self.assertEqual(item.quantity, 1000)
        # self.assertEqual(unicode(item.uom), u'pi縦e')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_char2(self, filename='test_char2.csv'):
        """ Use custom command to parse file with range of unicode characters """
        self.command(filename)
        item = self.get_item(u"Cet élément est utilisé par quelqu'un d'autre et ne peux être modifié")
        self.assertEqual(item.description, 
                         "TENTE FAMILIALE, 12 m_, COMPLETE (tapis de sol/double toit)")
        self.assertEqual(item.quantity, 101)
        self.assertEqual(unicode(item.uom), u'删除当前图片')
        self.assertEqual(item.organisation.name, 'AID-France')
        Item.objects.all().delete()

    def test_duplicate(self, filename='test_duplicate.csv'):
        """ Use custom command to upload file and parse it into Items """
        self.command(filename)
        items = Item.objects.all().order_by('code_share')
        # Check a couple of the fields in Item    
        self.assertEqual(len(items), 3)
        codes = (u'bucket', u'tent', u'watercan')
        for i, item in enumerate(items):
            self.assertEqual(item.code_share, codes[i])
        Item.objects.all().delete()
