#!/usr/bin/env python

from cStringIO import StringIO
from datetime import date, datetime
import unittest

from csvconvert import read_csv, write_csv
from objects import ADURecord
from structure import ADUFORMAT


class TestCSVConverter(unittest.TestCase):

    def test_round_trip(self):
        r = ADURecord()
        r.Record_Type = 'D'
        r.Gift_Date = date(2011, 10, 4)
        r.Title_1 = u"Mrs."
        r.First_Name_1 = u"Mary"
        r.Last_Name_1 = u"Ferguson"
        r.Street_Number = u"123"
        r.Street_Name = u"1st St"
        r.Apartment_Number = u""
        r.City = u"New York"
        r.State = u""
        r.Country = u""
        r.Zip_Code = u"11223"
        r.Telephone_Number_1 = u"2121234567"
        r.Telephone_Type_1 = 'H'
        r.Email_Address_1 = u"abc@gmail.com"
        r.Pledge_Number = 3000123971
        r.Pledge_Time = datetime(2011, 9, 15, 12, 11, 25)
        r.Gift_Kind = 'OP'
        r.Activity = 'AW'
        r.Campaign = 'O'
        r.Pledge_Amount = 300
        
        original = [r]
        sio = StringIO()
        write_csv(original, sio)
        new = read_csv(sio)
        for rec1, rec2 in zip(original, new):
            for field in ADUFORMAT:
                name = field[0]
                self.assertEqual(rec1._data.get(name), rec2._data.get(name))


if __name__ == '__main__':
    unittest.main()
