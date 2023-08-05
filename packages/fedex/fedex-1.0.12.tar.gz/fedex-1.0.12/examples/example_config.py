"""
This file holds various configuration options used for all of the examples.

You will need to change the values below to match your test account.
"""
import os
import sys
# Use the fedex directory included in the downloaded package instead of
# any globally installed versions.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fedex.config import FedexConfig

# Change these values to match your testing account/meter number.
CONFIG_OBJ = FedexConfig(key='35khOMxLwlMgovlc',
                         password='16WukaZdPp9epvFtDgG2tj5eF',
                         account_number='510087127',
                         meter_number='118506046',
                         use_test_server=True)