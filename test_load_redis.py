import mock
import unittest
import redis
import fakeredis

from load_redis import uniq,valid
from ddt import ddt,data


@ddt
class TestLoad(unittest.TestCase):

    def setUp(self):
        data={'Chicken Salad':'chicken,spinach','Burger':'bun, ground beef, cheese'}
        self.redis = fakeredis.FakeStrictRedis()

        for point in data:
            self.redis.set(point,data[point])

    def tearDown(self):
        self.redis.flushall()

    #Test uniq function using the mocked redis instance populated in setUp
    @data(['Burger',False],['Spaghetti',True],['Chicken Salad',False])
    def test_uniq(self,test_data):
        self.assertTrue(uniq(self.redis,test_data[0]) == test_data[1])

    #Test the valid dish entry method
    @data([{"summary":1,'ingredients':'t'},True],[{"summary":'g'},False])
    def test_valid(self,test_data):
        self.assertTrue( valid(test_data[0]) == test_data[1])

if __name__ == "__main__":
    unittest.main()
