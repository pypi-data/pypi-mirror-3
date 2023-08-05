# Copyright 2011 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.test import (
    TestCase as DjangoTestCase,
    TransactionTestCase as DjangoTransactionTestCase,
    )
from testtools import TestCase as TesttoolsTestCase

from django_factory.factory import Factory

__all__ = [
    'TestCase',
    'TransactionTestCase',
    ]


class TestCase(DjangoTestCase, TesttoolsTestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.factory = Factory(test_case=self)


class TransactionTestCase(DjangoTransactionTestCase, TesttoolsTestCase):

    def setUp(self):
        super(TransactionTestCase, self).setUp()
        self.factory = Factory(test_case=self)
