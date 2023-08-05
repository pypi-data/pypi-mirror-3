#
# Copyright (C) 2009-2010  Nexedi SA
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import unittest
from ZODB.tests.StorageTestBase import StorageTestBase
from ZODB.tests.TransactionalUndoStorage import TransactionalUndoStorage
from ZODB.tests.ConflictResolution import ConflictResolvingTransUndoStorage

from neo.tests.zodb import ZODBTestCase

class UndoTests(ZODBTestCase, StorageTestBase, TransactionalUndoStorage,
        ConflictResolvingTransUndoStorage):
    pass

# Don't run this test. It cannot run with pipelined store, and is not executed
# on Zeo - but because Zeo doesn't have an iterator, while Neo has.
# Note that it is possible to run this test on Neo with a simple fix:
# instead of expecting "store" to return object's serial, it should
# just load it after commit, and keep its serial.
# When iterator is fully implemented in Neo, a fork of that test should be
# done with above fix.
del TransactionalUndoStorage.checkTransactionalUndoIterator

if __name__ == "__main__":
    suite = unittest.makeSuite(UndoTests, 'check')
    unittest.main(defaultTest='suite')

