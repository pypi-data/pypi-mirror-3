"""
Base classes and unit tests for general formats-related modules. Look within
the submodules for each format for their own respective serialization and
deserialization tests.
"""
import unittest
from emds.data_structures import MarketOrder, MarketOrderList, MarketHistoryList, MarketHistoryEntry
from emds.common_utils import  UTC_TZINFO, now_dtime_in_utc
from emds.formats.unified.unified_utils import parse_datetime

class CommonUtilsCase(unittest.TestCase):
    """
    Tests the stuff in the common_utils module.
    """
    def test_datetime_parsing(self):
        """
        Run through a few different scenarios with datetime parsing.
        """
        pdtime = parse_datetime("2012-06-19T22:41:52+01:00")
        # dtime string had +1 tz offset. -1 gets us back to UTC. The parser
        # converts local times to UTC, so make sure this matches up.
        self.assertEqual(pdtime.hour, 21)
        # Make sure it converted to UTC.
        self.assertEqual(pdtime.tzinfo, UTC_TZINFO)


class BaseSerializationCase(unittest.TestCase):
    """
    This is a base class that provides some convenient test data for the
    various formats to use in their respective unit tests.
    """

    def setUp(self):
        self.order_list = MarketOrderList()
        self.order1 = MarketOrder(
            order_id=2413387906,
            is_bid=True,
            region_id=10000068,
            solar_system_id=30005316,
            station_id=60011521,
            type_id=10000068,
            price=52875,
            volume_entered=10,
            volume_remaining=4,
            minimum_volume=1,
            order_issue_date=now_dtime_in_utc(),
            order_duration=90,
            order_range=5,
            generated_at=now_dtime_in_utc()
        )
        self.order_list.add_order(self.order1)
        # This order isn't added, but it's here for the test to add.
        self.order2 = MarketOrder(
            order_id=1234566,
            is_bid=False,
            region_id=10000032,
            solar_system_id=30005312,
            station_id=60011121,
            type_id=10000067,
            price=52,
            volume_entered=10,
            volume_remaining=500,
            minimum_volume=1,
            order_issue_date=now_dtime_in_utc(),
            order_duration=90,
            order_range=5,
            generated_at=now_dtime_in_utc()
        )

        self.history = MarketHistoryList()
        self.history1 = MarketHistoryEntry(
            type_id=2413387906,
            region_id=10000068,
            historical_date=now_dtime_in_utc(),
            num_orders=5,
            low_price=5.0,
            high_price=10.5,
            average_price=7.0,
            total_quantity=200,
            generated_at=now_dtime_in_utc(),
        )
        self.history.add_entry(self.history1)
        # This order isn't added, but it's here for the test to add.
        self.history2 = MarketHistoryEntry(
            type_id=1413387203,
            region_id=10000067,
            historical_date=now_dtime_in_utc(),
            num_orders=50,
            low_price=50.0,
            high_price=100.5,
            average_price=70.0,
            total_quantity=2000,
            generated_at=now_dtime_in_utc(),
        )
