import unittest
from weather import DailyWeather, HistoricalWeather, Country, load_data
import json
import re
from datetime import date, timedelta, datetime
import os


class TestUtil(unittest.TestCase):
    def assert_public_methods(self, class_, allowed_methods):
        methods = list(class_.__dict__.keys())
        public_methods = list(filter(lambda x: not x.startswith('_'), methods))
        self.assertCountEqual(allowed_methods, public_methods,
                              'You should not add any new public methods')

    def assert_public_attrs(self, object_, allowed_attrs):
        attrs = list(object_.__dict__.keys())
        public_attrs = list(filter(lambda x: not x.startswith('_'), attrs))
        self.assertCountEqual(allowed_attrs, public_attrs,
                              'You should not add new public attrs')

    def assert_docstring(self):
        pass

    def assert_object(self, object_, attrs, exps):
        for i in range(len(attrs)):
            attr = attrs[i]
            val = getattr(object_, attr)
            exp = exps[i]
            self.assertEqual(exp, val,
                             f'{attr} does not match Exp: {exp} Act: {val}')


class TestWeather(TestUtil):
    def setUp(self) -> None:
        self.sample = DailyWeather((10, 10, 30), (-1, -1, -1))

    def tearDown(self) -> None:
        self.sample = DailyWeather((10, 10, 30), (-1, -1, -1))

    def test_str(self):
        numbers = re.compile("-?\d+")
        temp = str(self.sample)
        self.assertListEqual(['10', '10', '30', '-1', '-1', '-1'],
                             numbers.findall(temp),
                             'You should include all six numbers for weather')

    def test_public_methods(self):
        self.assert_public_methods(DailyWeather, [])

    def test_public_attrs(self):
        self.assert_public_attrs(self.sample, ['avg_temp', 'low_temp',
                                               'high_temp', 'precipitation',
                                               'snowfall', 'rainfall'])

    def test_init(self):
        attrs = ['avg_temp', 'low_temp', 'high_temp',
                 'precipitation', 'snowfall', 'rainfall']
        exps = [10, 10, 30, -1, -1, -1]
        self.assert_object(self.sample, attrs, exps)


class TestHistoricalWeather(TestUtil):
    def setUp(self) -> None:
        self.sample = HistoricalWeather('test1', (10, 20))
        self.sample_data = DailyWeather((10, 10, 30), (-1, -1, -1))
        self.sample_data_2 = DailyWeather((100, 100, 300), (10, 10, 30))
        self.sample_data_3 = DailyWeather((1000, 1000, 3000), (0, 0, 0))
        self.months = [date(2008, i, 1).strftime('%B')[:3] for i in
                       range(1, 13, 1)]
        self.today = date.today()

    def tearDown(self) -> None:
        pass

    def test_public_methods(self):
        self.assert_public_methods(HistoricalWeather,
                                   ['add_weather', 'retrieve_weather',
                                    'record_high', 'monthly_average',
                                    'contiguous_precipitation',
                                    'percentage_snowfall'])

    def test_public_attrs(self):
        self.assert_public_attrs(self.sample,
                                 ['name', 'coordinates'])

    def test_init(self):
        self.assert_object(self.sample, ['name', 'coordinates', '_records'],
                           ['test1', (10, 20), {}])

    def test_add_weather_1(self):
        self.sample.add_weather(date.today(), self.sample_data)
        self.assert_object(self.sample.retrieve_weather(date.today()),
                           ['avg_temp', 'low_temp', 'high_temp',
                            'precipitation', 'snowfall', 'rainfall'],
                           [10, 10, 30, -1, -1, -1])

    def test_add_weather_2(self):
        self.sample.add_weather(self.today, self.sample_data)
        self.sample.add_weather(self.today, self.sample_data_2)
        self.assert_object(self.sample.retrieve_weather(date.today()),
                           ['avg_temp', 'low_temp', 'high_temp',
                            'precipitation', 'snowfall', 'rainfall'],
                           [10, 10, 30, -1, -1, -1])

    def retrieve_weather(self):
        self.assertIsNone(self.sample.retrieve_weather(date.today()),
                          'There is no record for today you should return None')

    def test_record_high_1(self):
        self.sample.add_weather(self.today, self.sample_data)
        max_temp = self.sample.record_high(self.today.month, self.today.day)
        self.assertEqual(self.sample_data.high_temp, max_temp,
                         'There is only one record and you should return it')

    def test_record_high_2(self):
        last_year = date(self.today.year - 1, self.today.month, self.today.day)
        self.sample.add_weather(self.today, self.sample_data)
        self.sample.add_weather(last_year, self.sample_data_2)
        max_temp = self.sample.record_high(self.today.month, self.today.day)
        self.assertEqual(self.sample_data_2.high_temp, max_temp,
                         'There are two records having the same month and day, '
                         'you should return the max temperature')

    def test_monthly_average_1(self):
        exp = {mon: None for mon in self.months}
        self.assertDictEqual(exp, self.sample.monthly_average(),
                             'Since there are no data in it you should map every month to None')

    def test_monthly_average_2(self):
        today = date.today()
        month = self.months[today.month - 1]
        self.sample.add_weather(today, self.sample_data)
        self.sample.add_weather(date(today.year - 1, today.month, today.day),
                                self.sample_data_2)
        exp = {mon: None if mon != month else 55 for mon in self.months}
        self.assertDictEqual(exp, self.sample.monthly_average(),
                             'Since there are only two records which are in the same month you should return return the average and make remined to be None')

    def test_monthly_average_3(self):
        today = date.today()
        for i in range(1, 13, 1):
            for j in range(1, i + 1, 1):
                date_1 = date(today.year, i, j)
                data_1 = DailyWeather((j, j, j), (-1, -1, -1))
                self.sample.add_weather(date_1, data_1)
        exp = {self.months[i]: 1.0 + (0.5 * i) for i in range(12)}
        self.assertDictEqual(exp, self.sample.monthly_average())

    def test_contiguous_precipitation_1(self):
        today = date.today()
        self.sample.add_weather(today, self.sample_data)
        res = self.sample.contiguous_precipitation()
        self.assertTupleEqual((today, 1), res,
                              'Case when there is only one record')

    def test_contiguous_precipitation_2(self):
        today = date.today()
        for i in range(10, 0, -1):
            date_ = date(today.year, 1, i)
            self.sample.add_weather(date_, self.sample_data)
        res = self.sample.contiguous_precipitation()
        self.assertTupleEqual((date(today.year, 1, 1), 10), res,
                              'Testing records inserted in the order')

    def test_contiguous_precipitation_3(self):
        for i in range(1, 6, 1):
            date_ = date(2000 + i, 1, i)
            self.sample.add_weather(date_, self.sample_data)
        res = self.sample.contiguous_precipitation()
        self.assertTrue(res in [(date(2000 + i, 1, i), 1) for i in range(1, 6)],
                        'Since there is no continuous precipitation, all of date has a length of 1')

    def test_contiguous_precipitation_4(self):
        """
        Single break
        2000-1-1
        2000-1-2
        Break No Precipitation
        2000-1-4
        2000-1-5
        2000-1-6
        """
        acc = []
        for i in range(1, 7, 1):
            date_ = date(2000, 1, i)
            data_ = DailyWeather((10, 20, 30),
                                 (-1, -1, -1)) if i != 3 else DailyWeather(
                (10, 20, 30), (0, 0, 0))
            acc.append((date_, data_))
        acc = acc[::-1]
        for val in acc:
            date_, data_ = val
            self.sample.add_weather(date_, data_)
        self.assertTupleEqual((date(2000, 1, 4), 3),
                              self.sample.contiguous_precipitation())

    def test_contiguous_precipitation_5(self):
        """
        Two breaks
        2000-1-1
        2000-1-2
        Break
        2000-1-4
        Break
        2000-1-6
        2000-1-7
        2000-1-8
        """
        acc = []
        for i in range(1, 9, 1):
            date_ = date(2000, 1, i)
            data_ = DailyWeather((10, 20, 30),
                                 (-1, -1, -1)) if i not in [3, 5] else DailyWeather(
                (10, 20, 30), (0, 0, 0))
            acc.append((date_, data_))
        for val in acc:
            date_, data_ = val
            self.sample.add_weather(date_, data_)
        self.assertTupleEqual((date(2000, 1, 6), 3),
                              self.sample.contiguous_precipitation())

    def test_percentage_snowfall_1(self):
        self.sample.add_weather(date.today(), self.sample_data_2)
        res = self.sample.percentage_snowfall()
        self.assertEqual(0.75, res)

    def test_percentage_snowfall_2(self):
        self.sample.add_weather(date.today(), self.sample_data)
        self.sample.add_weather(date.today() + timedelta(days=1),
                                self.sample_data_2)
        self.sample.add_weather(date.today() + timedelta(days=2),
                                self.sample_data_3)
        res = self.sample.percentage_snowfall()
        self.assertEqual(0.75, res, 'The trace amount is not considered')

    def test_percentage_snowfall_3(self):
        for i in range(1, 5, 1):
            data_ = DailyWeather((10, 10, 10), (10, 10 * i, 5))
            date_ = date.today() + timedelta(days=i)
            self.sample.add_weather(date_, data_)
        res = self.sample.percentage_snowfall()
        self.assertAlmostEqual(1 / 6, res)

    def test_percentage_snowfall_4(self):
        for i in range(1, 5, 1):
            data_ = DailyWeather((10, 10, 10), (1, 1, -1))
            date_ = date.today() + timedelta(days=i)
            self.sample.add_weather(date_, data_)
        res = self.sample.percentage_snowfall()
        self.assertEqual(0.0, res,
                         'All the snowing are trace thus you should return 0')

    def test_percentage_snowfall_5(self):
        for i in range(1, 5, 1):
            data_ = DailyWeather((10, 10, 10), (1, -1, 1))
            date_ = date.today() + timedelta(days=i)
            self.sample.add_weather(date_, data_)
        res = self.sample.percentage_snowfall()
        self.assertEqual(1.0, res,
                         'All the raining are trace thus you should return 1')


class TestCountry(TestUtil):
    def setUp(self) -> None:
        self.sample = Country('Test')
        self.d1 = DailyWeather((10, 20, 30), (-1, -1, -1))
        self.d2 = DailyWeather((100, 20, 30), (-1, -1, -1))
        self.h1 = HistoricalWeather('Test Sample 1', (10, 20))
        self.h2 = HistoricalWeather('Test Sample 2', (15, 20))

    def tearDown(self) -> None:
        pass

    def test_public_methods(self):
        self.assert_public_methods(Country, ['add_history', 'retrieve_history',
                                             'snowiest_location',
                                             'generate_summary'])

    def test_public_attrs(self):
        self.assert_public_attrs(self.sample, ['name'])

    def test_add_history(self):
        self.sample.add_history(self.h1)
        self.assert_object(self.sample.retrieve_history('Test Sample 1'),
                           ['name', 'coordinates'],
                           ['Test Sample 1', (10, 20)])
        temp = HistoricalWeather('Test Sample 1', (20, 30))
        self.sample.add_history(temp)
        self.assert_object(self.sample.retrieve_history('Test Sample 1'),
                           ['name', 'coordinates'],
                           ['Test Sample 1', (10, 20)])

    def test_retrieve_history(self):
        self.assertIsNone(self.sample.retrieve_history('Test'))

    def test_snowiest_location_1(self):
        self.assertTupleEqual((None, None), self.sample.snowiest_location(),
                              'You should return None when there is no location added to the Country')

    def test_snowiest_location_2(self):
        self.sample.add_history(self.h1)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 1, -1)))
        res = self.sample.snowiest_location()
        self.assertEqual(('Test Sample 1', 0), res,
                         'There is only one location you should it')

    def test_snowiest_location_3(self):
        self.sample.add_history(self.h1)
        self.sample.add_history(self.h2)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 1, -1)))
        self.h2.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 1, -1)))
        res = self.sample.snowiest_location()
        self.assertTrue(res in [('Test Sample 1', 0), ('Test Sample 2', 0)])

    def test_snowiest_location_4(self):
        self.sample.add_history(self.h1)
        self.sample.add_history(self.h2)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 1, 0)))
        self.h2.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 0, 1)))
        res = self.sample.snowiest_location()
        self.assertEqual(('Test Sample 2', 1), res,
                         'You should return the snowiest one')

    def test_snowiest_location_5(self):
        self.sample.add_history(self.h1)
        self.sample.add_history(self.h2)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 0, 1)))
        self.h2.add_weather(date.today(), DailyWeather((10, 10, 10), (1, -1, 1)))
        res = self.sample.snowiest_location()
        self.assertTrue(res in [('Test Sample 1', 1.0), ('Test Sample 2', 1.0)],
                        'You should still handle for trace')

    def test_snowiest_location_6(self):
        self.sample.add_history(self.h1)
        self.sample.add_history(self.h2)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 1, 0)))
        self.h2.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 10, 20)))
        self.h2.add_weather(date.today() + timedelta(days=1),
                            DailyWeather((20, 30, 40), (1, 50, 20)))
        res = self.sample.snowiest_location()
        self.assertEqual(('Test Sample 2', 0.4), res,
                         'The first location has no snow you should return accumulate result of h2')

    def test_snowiest_location_7(self):
        self.sample.add_history(self.h1)
        self.sample.add_history(self.h2)
        self.h1.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 0, 1)))
        self.h2.add_weather(date.today(), DailyWeather((10, 10, 10), (1, 10, 20)))
        self.h2.add_weather(date.today() + timedelta(days=1),
                            DailyWeather((20, 30, 40), (1, 50, 20)))
        res = self.sample.snowiest_location()
        self.assertEqual(('Test Sample 1', 1.0), res,
                         'The first location has snow of 1 percent')


class TestLoadData(TestUtil):
    def setUp(self) -> None:
        self.curr_dir = os.getcwd()
        self.data_dir = os.path.join(os.getcwd(), 'student_data')

    def tearDown(self) -> None:
        pass

    def test_empty_file(self):
        with open(os.path.join(self.data_dir, 'empty_sample_data.csv')) as f:
            res = load_data(f)
            self.assertIsNone(res,
                              'There is no data in the file you should return None')

    def test_single_file(self):
        with open(os.path.join(self.data_dir, 'single_sample_data.csv')) as f:
            res = load_data(f)
            self.assertEqual('YORK', res.name,
                             'You should load correct station name')
            weather = res.retrieve_weather(date(2019, 12, 25))
            self.assert_object(weather, ['avg_temp', 'low_temp', 'high_temp',
                                         'precipitation', 'rainfall', 'snowfall'],
                               [7.3, -2.1, 13.6, 25.3, 0.0, 25.1])

    def test_ill_file(self):
        with open(os.path.join(self.curr_dir, 'ill_form.csv')) as f:
            res = load_data(f)
            self.assertIsNone(res, "All the rows in the file are ill-formed you should not be able to create any instace")

    def test_ill_file_2(self):
        with open(os.path.join(self.curr_dir, 'ill_form_2.csv')) as f:
            res = load_data(f)
            self.assertIsNotNone(res, 'You should load non-ill data')
            self.assertEqual('YORK', res.name)
            self.assertEqual((43.7735, 79.5019,), res.coordinates)
            weather = res.retrieve_weather(date(2019, 12, 25))
            self.assert_object(weather, ['avg_temp', 'low_temp', 'high_temp',
                                         'precipitation', 'rainfall',
                                         'snowfall'],
                               [7.3, -2.1, 13.6, 25.3, 0.0, 25.1])

    def test_trace(self):
        with open(os.path.join(self.curr_dir, 'trace.csv')) as f:
            res = load_data(f)
            self.assertEqual((48.3809, 89.2477), res.coordinates)
            self.assertEqual('THUNDER BAY', res.name)
            with open(os.path.join(self.curr_dir, 'trace.json')) as json_file:
                data = json.load(json_file)['THUNDER BAY']
                for date_str in data:
                    attrs = []
                    exps = []
                    weather = res.retrieve_weather(datetime.strptime(date_str, "%m/%d/%Y").date())
                    for k, v in data[date_str].items():
                        attrs.append(k)
                        exps.append(v)
                    self.assert_object(weather, attrs, exps)

    def test_sample_file(self):
        with open(os.path.join(self.data_dir, 'small_sample_data.csv')) as f:
            res = load_data(f)
            self.assertEqual((48.3809, 89.2477), res.coordinates)
            self.assertEqual('THUNDER BAY', res.name)
            with open(os.path.join(self.curr_dir, 'small_sample.json')) as json_file:
                data = json.load(json_file)['THUNDER BAY']
                for date_str in data:
                    attrs = []
                    exps = []
                    weather = res.retrieve_weather(
                        datetime.strptime(date_str, "%m/%d/%Y").date())
                    for k, v in data[date_str].items():
                        attrs.append(k)
                        exps.append(v)
                    self.assert_object(weather, attrs, exps)


if __name__ == '__main__':
    unittest.main(verbosity=True)
