import unittest

import provision.nodelib as nodelib

'''
Below are some examples of sizes from real providers:

>>> [(s.name, s.id) for s in devstack_driver().list_sizes()]
[('m1.medium', '3'), ('m1.micro', '0'), ('m1.small', '2'), ('m1.large', '4'), ('m1.tiny', '1'), ('m1.xlarge', '5')]

>>> [(s.name, s.id) for s in rackspace_driver().list_sizes()]
[('256 server', '1'), ('512 server', '2'), ('1GB server', '3'), ('2GB server', '4'), ('4GB server', '5'), ('8GB server', '6'), ('15.5GB server', '7'), ('30GB server', '8')]

>>> [(s.name, s.id) for s in aws_driver().list_sizes()]
[('Medium Instance', 'm1.medium'), ('Large Instance', 'm1.large'), ('High-CPU Extra Large Instance', 'c1.xlarge'), ('Small Instance', 'm1.small'), ('High-CPU Medium Instance', 'c1.medium'), ('Extra Large Instance', 'm1.xlarge'), ('High-Memory Extra Large Instance', 'm2.xlarge'), ('Micro Instance', 't1.micro'), ('High-Memory Quadruple Extra Large Instance', 'm2.4xlarge'), ('High-Memory Double Extra Large Instance', 'm2.2xlarge')]
'''

class MockSize(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

class Test(unittest.TestCase):

    def setUp(self):
        self.name = '256 server'
        self.sizes = map(MockSize, ['512 server', '256 server', '1GB server'])

    def test_size_from_name(self):
        assert '256 server' == nodelib.size_from_name(
            self.name, self.sizes).name
