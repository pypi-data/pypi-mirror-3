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
from mock import Mock
from neo.tests.storage.testStorageDBTests import StorageDBTests
from neo.storage.database.btree import BTreeDatabaseManager

class StorageBTreeTests(StorageDBTests):

    def getDB(self, reset=0):
        # db manager
        db = BTreeDatabaseManager('')
        db.setup(reset)
        return db

del StorageDBTests

if __name__ == "__main__":
    unittest.main()
