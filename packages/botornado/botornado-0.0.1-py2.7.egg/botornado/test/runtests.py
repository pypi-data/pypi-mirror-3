#!/usr/bin/env python
import unittest

TEST_MODULES = [
    'botornado.test.connection_test',
    'botornado.test.s3.connection_test',
    'botornado.test.sqs.connection_test',
]

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

if __name__ == '__main__':
    import tornado.testing
    tornado.testing.main()

# vim:set ft=python sw=4 :
