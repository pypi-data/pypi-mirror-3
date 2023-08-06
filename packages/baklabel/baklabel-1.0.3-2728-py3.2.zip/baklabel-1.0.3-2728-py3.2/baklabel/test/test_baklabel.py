import unittest
from datetime import date
try:
    from baklabel import Grandad
except ImportError:
    from baklabel.baklabel import Grandad

class test_baklabel(unittest.TestCase):
    """
    def __init__(self,
                  backupday=date.today(),
                   server_name=SERVER_NAME,
                    new_year_month=NEW_YEAR_MONTH,
                     eoy_label=EOY_LABEL,
                      append_eoy_year=APPEND_YEAR_TO_EOY_LABEL,
                       append_eom_year=APPEND_YEAR_TO_EOM_LABEL,
                        weekly_day=WEEKLY_DAY,
                         smallhours=SMALLHOURS):
    """

    def test_new_year_day_eom_year_bad_str(self):
        """ 69 """
        dday = '2040/1'
        try:
            tsto = Grandad(dday,
                                    append_eom_year=True)
        except ValueError:
            dday = '2040/1/1'
            tsto = Grandad(dday,
                                    append_eom_year=True)
            expected = 'sun'
            result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_eom_year_str(self):
        """ 68 """
        dday = '2040/2/28'
        expected = 'tue'
        tsto = Grandad(dday,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_leap_year_eom_year_str(self):
        """ 67 """
        dday = '2040/2/29'
        expected = 'feb_2040'
        tsto = Grandad(dday,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_eoy_true_eom_false_str(self):
        """ 66 """
        dday = '2040/12/31'
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eoy_year=True,
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_eoy_false_eom_true_str(self):
        """ 65 """
        dday = '2040/12/31'
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eoy_year=False,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_default_eoy_eom_false_str(self):
        """ 64 """
        dday = '2040/12/31'
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_forced_eoy_eom_false_str(self):
        """ 63 """
        dday = '2040/12/31'
        expected = 'eoy_2040'
        tsto = Grandad(dday, eoy_label='eoy',
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_new_year_day_eom_year(self):
        """ 62 """
        dday = date(2040, 1, 1)
        expected = 'sun'
        tsto = Grandad(dday,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_eom_year(self):
        """ 61 """
        dday = date(2040, 2, 28)
        expected = 'tue'
        tsto = Grandad(dday,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_leap_year_eom_year(self):
        """ 60 """
        dday = date(2040, 2, 29)
        expected = 'feb_2040'
        tsto = Grandad(dday,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_eoy_true_eom_false(self):
        """ 59 """
        dday = date(2040, 12, 31)
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eoy_year=True,
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_eoy_false_eom_true(self):
        """ 58 """
        dday = date(2040, 12, 31)
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eoy_year=False,
                                append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_default_eoy_eom_false(self):
        """ 57 """
        dday = date(2040, 12, 31)
        expected = 'dec_2040'
        tsto = Grandad(dday,
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_forced_eoy_eom_false(self):
        """ 56 """
        dday = date(2040, 12, 31)
        expected = 'eoy_2040'
        tsto = Grandad(dday, eoy_label='eoy',
                                append_eom_year=False)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_mar_year(self):
        """ 55 """
        dday = date(2040, 3, 31)
        expected = 'mar_2040'
        tsto = Grandad(dday, append_eom_year=True)
        result = tsto.label()
        self.assertEqual(result, expected)

    # month 13 generates ValueError as expected
    def test_bad_date(self):
        try:
            dday = '2040-13-8'
            tsto = Grandad(dday)
        except ValueError as e:
            dday = '2040-8-13'
            expected = 'mon'
            tsto = Grandad(dday)
            result = tsto.label()
        self.assertEqual(result, expected)

    def test_2040313_time_trigger_late(self):
        """ 54 """
        dday = date(2040, 3, 13)
        expected = 'mon'
        # note this must be run before 23:00 to succeed
        tsto = Grandad(dday, smallhours=23)
        result = tsto.label()
        self.assertEqual(result, expected)
        # now prove dday is Tuesday
        expected = 'tue'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_2040313_time_trigger_early(self):
        """ 53 """
        dday = date(2040, 3, 13)
        expected = 'tue'
        # note this must be run after 02:00 to succeed
        tsto = Grandad(dday, smallhours=2)
        result = tsto.label()
        self.assertEqual(result, expected)
        # now prove dday is Tuesday
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)


    def test_confirm_none_eq_today(self):
        """ 52 """
        dday = None
        tsto = Grandad(dday)
        result = tsto.label()
        expday = date.fromordinal(date.today().toordinal())
        expobj = Grandad(expday)
        expected = expobj.label()
        self.assertEqual(result, expected)

    def test_confirm_blank_eq_today(self):
        """ 51 """
        dday = ''
        tsto = Grandad(dday)
        result = tsto.label()
        expday = date.fromordinal(date.today().toordinal())
        expobj = Grandad(expday)
        expected = expobj.label()
        self.assertEqual(result, expected)

    def test_confirm_number_adds_to_today(self):
        """ 50 """
        dday = " +3 "
        tsto = Grandad(dday)
        result = tsto.label()
        expday = date.fromordinal(date.today().toordinal() + 3)
        expobj = Grandad(expday)
        expected = expobj.label()
        self.assertEqual(result, expected)

    def test_confirm_number_subtracts_from_today(self):
        """ 49 """
        dday = " -1 "
        tsto = Grandad(dday)
        result = tsto.label()
        expday = date.fromordinal(date.today().toordinal() - 1)
        expobj = Grandad(expday)
        expected = expobj.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_next_thu_a(self):
        """ 48 """
        dday = date(2040, 3, 8)
        expected = 'a_thu'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_wed_a(self):
        """ 47 """
        dday = date(2040, 3, 7)
        expected = 'a_wed'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_tue_a(self):
        """ 46 """
        dday = date(2040, 3, 6)
        expected = 'a_tue'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_mon_a(self):
        """ 45 """
        dday = date(2040, 3, 5)
        expected = 'a_mon'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_sun_a(self):
        """ 44 """
        dday = date(2040, 3, 4)
        expected = 'a_sun'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_sat_a(self):
        """ 43 """
        dday = date(2040, 3, 3)
        expected = 'a_sat'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_fri_a(self):
        """ 42 """
        dday = date(2040, 3, 2)
        expected = 'a_fri'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_thu_a(self):
        """ 41 """
        dday = date(2040, 3, 1)
        expected = 'a_thu'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_1st_thu_weekly_day_a(self):
        """ 40 """
        dday = date(2040, 3, 1)
        expected = 'a_thu_1'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=3)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_sun_weekly_day_a(self):
        """ 39 """
        dday = date(2040, 3, 11)
        expected = 'a_sun_2'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=6)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_beats_5th_sat_a(self):
        """ 38 """
        dday = date(2040, 3, 31)
        expected = 'a_mar'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=5)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_sat_weekly_day_a(self):
        """ 37 """
        dday = date(2040, 3, 24)
        expected = 'a_sat_4'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=5)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_3rd_thu_weekly_day_a(self):
        """ 36 """
        dday = date(2010, 3, 18)
        expected = 'a_thu_3'
        tsto = Grandad(dday, server_name='a',
                                weekly_day=3)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_new_year_day_a(self):
        """ 35 """
        dday = date(2040, 1, 1)
        expected = 'a_sun'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_a(self):
        """ 34 """
        dday = date(2040, 2, 28)
        expected = 'a_tue'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_leap_year_a(self):
        """ 33 """
        dday = date(2040, 2, 29)
        expected = 'a_feb'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_default_eoy_a(self):
        """ 32 """
        dday = date(2040, 12, 31)
        expected = 'a_dec_2040'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_forced_eoy_a(self):
        """ 31 """
        dday = date(2040, 12, 31)
        expected = 'a_eoy_2040'
        tsto = Grandad(dday, server_name='a',
                                eoy_label='eoy')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_mar_a(self):
        """ 30 """
        dday = date(2040, 3, 31)
        expected = 'a_mar'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_1st_friday_a(self):
        """ 29 """
        dday = date(2040, 3, 2)
        expected = 'a_fri_1'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_2nd_friday_a(self):
        """ 28 """
        dday = date(2040, 3, 9)
        expected = 'a_fri_2'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_3rd_friday_a(self):
        """ 27 """
        dday = date(2010, 3, 19)
        expected = 'a_fri_3'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_4th_friday_a(self):
        """ 26 """
        dday = date(2040, 3, 23)
        expected = 'a_fri_4'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_5th_friday_a(self):
        """ 25 """
        dday = date(2040, 3, 30)
        expected = 'a_fri_5'
        tsto = Grandad(dday, server_name='a')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_next_thu(self):
        """ 24 """
        dday = date(2040, 3, 8)
        expected = 'thu'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_wed(self):
        """ 23 """
        dday = date(2040, 3, 7)
        expected = 'wed'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_tue(self):
        """ 22 """
        dday = date(2040, 3, 6)
        expected = 'tue'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_mon(self):
        """ 21 """
        dday = date(2040, 3, 5)
        expected = 'mon'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_sun(self):
        """ 20 """
        dday = date(2040, 3, 4)
        expected = 'sun'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_sat(self):
        """ 19 """
        dday = date(2040, 3, 3)
        expected = 'sat'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_fri(self):
        """ 18 """
        dday = date(2040, 3, 2)
        expected = 'fri'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_no_weekly_day_thu(self):
        """ 17 """
        dday = date(2040, 3, 1)
        expected = 'thu'
        tsto = Grandad(dday, weekly_day=7)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_1st_thu_weekly_day(self):
        """ 16 """
        dday = date(2040, 3, 1)
        expected = 'thu_1'
        tsto = Grandad(dday, weekly_day=3)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_sun_weekly_day(self):
        """ 15 """
        dday = date(2040, 3, 11)
        expected = 'sun_2'
        tsto = Grandad(dday, weekly_day=6)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_beats_5th_sat(self):
        """ 14 """
        dday = date(2040, 3, 31)
        expected = 'mar'
        tsto = Grandad(dday, weekly_day=5)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_sat_weekly_day(self):
        """ 13 """
        dday = date(2040, 3, 24)
        expected = 'sat_4'
        tsto = Grandad(dday, weekly_day=5)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_force_thu_weekly_day(self):
        """ 12 """
        dday = date(2010, 3, 18)
        expected = 'thu_3'
        tsto = Grandad(dday, weekly_day=3)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_new_year_day(self):
        """ 11 """
        dday = date(2040, 1, 1)
        expected = 'sun'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb(self):
        """ 10 """
        dday = date(2040, 2, 28)
        expected = 'tue'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_feb_leap_year(self):
        """ 9 """
        dday = date(2040, 2, 29)
        expected = 'feb'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_default_eoy(self):
        """ 8 """
        dday = date(2040, 12, 31)
        expected = 'dec_2040'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_forced_eoy(self):
        """ 7 """
        dday = date(2040, 12, 31)
        expected = 'eoy_2040'
        tsto = Grandad(dday, eoy_label='eoy')
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_monthend_mar(self):
        """ 6 """
        dday = date(2040, 3, 31)
        expected = 'mar'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_1st_friday(self):
        """ 5 """
        dday = date(2040, 3, 2)
        expected = 'fri_1'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_2nd_friday(self):
        """ 4 """
        dday = date(2040, 3, 9)
        expected = 'fri_2'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_3rd_friday(self):
        """ 3 """
        dday = date(2010, 3, 19)
        expected = 'fri_3'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_4th_friday(self):
        """ 2 """
        dday = date(2040, 3, 23)
        expected = 'fri_4'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

    def test_5th_friday(self):
        """ 1 """
        dday = date(2040, 3, 30)
        expected = 'fri_5'
        tsto = Grandad(dday)
        result = tsto.label()
        self.assertEqual(result, expected)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



if __name__ == "__main__":

    import sys
    print('\nPython %s' % sys.version[0:3])
    unittest.main()


