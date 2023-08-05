# coding=utf-8
import unittest

import names


class TestScbNames(unittest.TestCase):

    def test_names(self):
        for gender in names.GENDERS:
            names.names(gender)

    def test_male(self):
        name_list = names.male()
        self.assertEqual(name_list[0], u'Aaron')
        self.assertEqual(name_list[-1], u'Ömer')

    def test_female(self):
        name_list = names.female()
        self.assertEqual(name_list[0], u'Abigail')
        self.assertEqual(name_list[-1], u'Ängla')


if __name__ == '__main__':
    unittest.main()
