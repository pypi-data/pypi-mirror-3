#
# Copyright (C) 2010  Nexedi SA
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
from neo.tests import NeoUnitTestBase
from neo.storage.transactions import Transaction, TransactionManager
from neo.storage.transactions import ConflictError, DelayedError


class TransactionTests(NeoUnitTestBase):

    def testInit(self):
        uuid = self.getNewUUID()
        ttid = self.getNextTID()
        tid = self.getNextTID()
        txn = Transaction(uuid, ttid)
        self.assertEqual(txn.getUUID(), uuid)
        self.assertEqual(txn.getTTID(), ttid)
        self.assertEqual(txn.getTID(), None)
        txn.setTID(tid)
        self.assertEqual(txn.getTID(), tid)
        self.assertEqual(txn.getObjectList(), [])
        self.assertEqual(txn.getOIDList(), [])

    def testRepr(self):
        """ Just check if the __repr__ implementation will not raise """
        uuid = self.getNewUUID()
        tid = self.getNextTID()
        txn = Transaction(uuid, tid)
        repr(txn)

    def testLock(self):
        txn = Transaction(self.getNewUUID(), self.getNextTID())
        self.assertFalse(txn.isLocked())
        txn.lock()
        self.assertTrue(txn.isLocked())
        # disallow lock more than once
        self.assertRaises(AssertionError, txn.lock)

    def testTransaction(self):
        txn = Transaction(self.getNewUUID(), self.getNextTID())
        oid_list = [self.getOID(1), self.getOID(2)]
        txn_info = (oid_list, 'USER', 'DESC', 'EXT', False)
        txn.prepare(*txn_info)
        self.assertEqual(txn.getTransactionInformations(), txn_info)

    def testObjects(self):
        txn = Transaction(self.getNewUUID(), self.getNextTID())
        oid1, oid2 = self.getOID(1), self.getOID(2)
        object1 = (oid1, 1, '1', 'O1', None)
        object2 = (oid2, 1, '2', 'O2', None)
        self.assertEqual(txn.getObjectList(), [])
        self.assertEqual(txn.getOIDList(), [])
        txn.addObject(*object1)
        self.assertEqual(txn.getObjectList(), [object1])
        self.assertEqual(txn.getOIDList(), [oid1])
        txn.addObject(*object2)
        self.assertEqual(txn.getObjectList(), [object1, object2])
        self.assertEqual(txn.getOIDList(), [oid1, oid2])

    def test_getObject(self):
        oid_1 = self.getOID(1)
        oid_2 = self.getOID(2)
        txn = Transaction(self.getNewUUID(), self.getNextTID())
        object_info = (oid_1, None, None, None, None)
        txn.addObject(*object_info)
        self.assertEqual(txn.getObject(oid_2), None)
        self.assertEqual(txn.getObject(oid_1), object_info)

class TransactionManagerTests(NeoUnitTestBase):

    def setUp(self):
        NeoUnitTestBase.setUp(self)
        self.app = Mock()
        # no history
        self.app.dm = Mock({'getObjectHistory': []})
        self.app.pt = Mock({'isAssigned': True})
        self.manager = TransactionManager(self.app)
        self.ltid = None

    def _getTransaction(self):
        tid = self.getNextTID(self.ltid)
        oid_list = [self.getOID(1), self.getOID(2)]
        return (tid, (oid_list, 'USER', 'DESC', 'EXT', False))

    def _storeTransactionObjects(self, tid, txn):
        for i, oid in enumerate(txn[0]):
            self.manager.storeObject(tid, None,
                    oid, 1, str(i), '0' + str(i), None)

    def _getObject(self, value):
        oid = self.getOID(value)
        serial = self.getNextTID()
        return (serial, (oid, 1, str(value), 'O' + str(value), None))

    def _checkTransactionStored(self, *args):
        calls = self.app.dm.mockGetNamedCalls('storeTransaction')
        self.assertEqual(len(calls), 1)
        calls[0].checkArgs(*args)

    def _checkTransactionFinished(self, tid):
        calls = self.app.dm.mockGetNamedCalls('finishTransaction')
        self.assertEqual(len(calls), 1)
        calls[0].checkArgs(tid)

    def _checkQueuedEventExecuted(self, number=1):
        calls = self.app.mockGetNamedCalls('executeQueuedEvents')
        self.assertEqual(len(calls), number)

    def testSimpleCase(self):
        """ One node, one transaction, not abort """
        uuid = self.getNewUUID()
        ttid = self.getNextTID()
        tid, txn = self._getTransaction()
        serial1, object1 = self._getObject(1)
        serial2, object2 = self._getObject(2)
        self.manager.register(uuid, ttid)
        self.manager.storeTransaction(ttid, *txn)
        self.manager.storeObject(ttid, serial1, *object1)
        self.manager.storeObject(ttid, serial2, *object2)
        self.assertTrue(ttid in self.manager)
        self.manager.lock(ttid, tid, txn[0])
        self._checkTransactionStored(tid, [object1, object2], txn)
        self.manager.unlock(ttid)
        self.assertFalse(ttid in self.manager)
        self._checkTransactionFinished(tid)

    def testDelayed(self):
        """ Two transactions, the first cause the second to be delayed """
        uuid = self.getNewUUID()
        ttid2 = self.getNextTID()
        ttid1 = self.getNextTID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        serial, obj = self._getObject(1)
        # first transaction lock the object
        self.manager.register(uuid, ttid1)
        self.manager.storeTransaction(ttid1, *txn1)
        self.assertTrue(ttid1 in self.manager)
        self._storeTransactionObjects(ttid1, txn1)
        self.manager.lock(ttid1, tid1, txn1[0])
        # the second is delayed
        self.manager.register(uuid, ttid2)
        self.manager.storeTransaction(ttid2, *txn2)
        self.assertTrue(ttid2 in self.manager)
        self.assertRaises(DelayedError, self.manager.storeObject,
                ttid2, serial, *obj)

    def testUnresolvableConflict(self):
        """ A newer transaction has already modified an object """
        uuid = self.getNewUUID()
        ttid2 = self.getNextTID()
        ttid1 = self.getNextTID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        serial, obj = self._getObject(1)
        # the (later) transaction lock (change) the object
        self.manager.register(uuid, ttid2)
        self.manager.storeTransaction(ttid2, *txn2)
        self.assertTrue(ttid2 in self.manager)
        self._storeTransactionObjects(ttid2, txn2)
        self.manager.lock(ttid2, tid2, txn2[0])
        # the previous it's not using the latest version
        self.manager.register(uuid, ttid1)
        self.manager.storeTransaction(ttid1, *txn1)
        self.assertTrue(ttid1 in self.manager)
        self.assertRaises(ConflictError, self.manager.storeObject,
                ttid1, serial, *obj)

    def testResolvableConflict(self):
        """ Try to store an object with the lastest revision """
        uuid = self.getNewUUID()
        tid, txn = self._getTransaction()
        serial, obj = self._getObject(1)
        next_serial = self.getNextTID(serial)
        # try to store without the last revision
        self.app.dm = Mock({'getObjectHistory': [next_serial]})
        self.manager.register(uuid, tid)
        self.manager.storeTransaction(tid, *txn)
        self.assertRaises(ConflictError, self.manager.storeObject,
                tid, serial, *obj)

    def testLockDelayed(self):
        """ Check lock delay """
        uuid1 = self.getNewUUID()
        uuid2 = self.getNewUUID()
        self.assertNotEqual(uuid1, uuid2)
        ttid2 = self.getNextTID()
        ttid1 = self.getNextTID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        serial1, obj1 = self._getObject(1)
        serial2, obj2 = self._getObject(2)
        # first transaction lock objects
        self.manager.register(uuid1, ttid1)
        self.manager.storeTransaction(ttid1, *txn1)
        self.assertTrue(ttid1 in self.manager)
        self.manager.storeObject(ttid1, serial1, *obj1)
        self.manager.storeObject(ttid1, serial1, *obj2)
        self.manager.lock(ttid1, tid1, txn1[0])
        # second transaction is delayed
        self.manager.register(uuid2, ttid2)
        self.manager.storeTransaction(ttid2, *txn2)
        self.assertTrue(ttid2 in self.manager)
        self.assertRaises(DelayedError, self.manager.storeObject,
                ttid2, serial1, *obj1)
        self.assertRaises(DelayedError, self.manager.storeObject,
                ttid2, serial2, *obj2)

    def testLockConflict(self):
        """ Check lock conflict """
        uuid1 = self.getNewUUID()
        uuid2 = self.getNewUUID()
        self.assertNotEqual(uuid1, uuid2)
        ttid2 = self.getNextTID()
        ttid1 = self.getNextTID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        serial1, obj1 = self._getObject(1)
        serial2, obj2 = self._getObject(2)
        # the second transaction lock objects
        self.manager.register(uuid2, ttid2)
        self.manager.storeTransaction(ttid2, *txn2)
        self.manager.storeObject(ttid2, serial1, *obj1)
        self.manager.storeObject(ttid2, serial2, *obj2)
        self.assertTrue(ttid2 in self.manager)
        self.manager.lock(ttid2, tid2, txn1[0])
        # the first get a conflict
        self.manager.register(uuid1, ttid1)
        self.manager.storeTransaction(ttid1, *txn1)
        self.assertTrue(ttid1 in self.manager)
        self.assertRaises(ConflictError, self.manager.storeObject,
                ttid1, serial1, *obj1)
        self.assertRaises(ConflictError, self.manager.storeObject,
                ttid1, serial2, *obj2)

    def testAbortUnlocked(self):
        """ Abort a non-locked transaction """
        uuid = self.getNewUUID()
        tid, txn = self._getTransaction()
        serial, obj = self._getObject(1)
        self.manager.register(uuid, tid)
        self.manager.storeTransaction(tid, *txn)
        self.manager.storeObject(tid, serial, *obj)
        self.assertTrue(tid in self.manager)
        # transaction is not locked
        self.manager.abort(tid)
        self.assertFalse(tid in self.manager)
        self.assertFalse(self.manager.loadLocked(obj[0]))
        self._checkQueuedEventExecuted()

    def testAbortLockedDoNothing(self):
        """ Try to abort a locked transaction """
        uuid = self.getNewUUID()
        ttid = self.getNextTID()
        tid, txn = self._getTransaction()
        self.manager.register(uuid, ttid)
        self.manager.storeTransaction(ttid, *txn)
        self._storeTransactionObjects(ttid, txn)
        # lock transaction
        self.manager.lock(ttid, tid, txn[0])
        self.assertTrue(ttid in self.manager)
        self.manager.abort(ttid)
        self.assertTrue(ttid in self.manager)
        for oid in txn[0]:
            self.assertTrue(self.manager.loadLocked(oid))
        self._checkQueuedEventExecuted(number=0)

    def testAbortForNode(self):
        """ Abort transaction for a node """
        uuid1 = self.getNewUUID()
        uuid2 = self.getNewUUID()
        self.assertNotEqual(uuid1, uuid2)
        ttid1 = self.getNextTID()
        ttid2 = self.getNextTID()
        ttid3 = self.getNextTID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        tid3, txn3 = self._getTransaction()
        self.manager.register(uuid1, ttid1)
        self.manager.register(uuid2, ttid2)
        self.manager.register(uuid2, ttid3)
        self.manager.storeTransaction(ttid1, *txn1)
        # node 2 owns tid2 & tid3 and lock tid2 only
        self.manager.storeTransaction(ttid2, *txn2)
        self.manager.storeTransaction(ttid3, *txn3)
        self._storeTransactionObjects(ttid2, txn2)
        self.manager.lock(ttid2, tid2, txn2[0])
        self.assertTrue(ttid1 in self.manager)
        self.assertTrue(ttid2 in self.manager)
        self.assertTrue(ttid3 in self.manager)
        self.manager.abortFor(uuid2)
        # only tid3 is aborted
        self.assertTrue(ttid1 in self.manager)
        self.assertTrue(ttid2 in self.manager)
        self.assertFalse(ttid3 in self.manager)
        self._checkQueuedEventExecuted(number=1)

    def testReset(self):
        """ Reset the manager """
        uuid = self.getNewUUID()
        tid, txn = self._getTransaction()
        ttid = self.getNextTID()
        self.manager.register(uuid, ttid)
        self.manager.storeTransaction(ttid, *txn)
        self._storeTransactionObjects(ttid, txn)
        self.manager.lock(ttid, tid, txn[0])
        self.assertTrue(ttid in self.manager)
        self.manager.reset()
        self.assertFalse(ttid in self.manager)
        for oid in txn[0]:
            self.assertFalse(self.manager.loadLocked(oid))

    def test_getObjectFromTransaction(self):
        uuid = self.getNewUUID()
        tid1, txn1 = self._getTransaction()
        tid2, txn2 = self._getTransaction()
        serial1, obj1 = self._getObject(1)
        serial2, obj2 = self._getObject(2)
        self.manager.register(uuid, tid1)
        self.manager.storeObject(tid1, serial1, *obj1)
        self.assertEqual(self.manager.getObjectFromTransaction(tid2, obj1[0]),
            None)
        self.assertEqual(self.manager.getObjectFromTransaction(tid1, obj2[0]),
            None)
        self.assertEqual(self.manager.getObjectFromTransaction(tid1, obj1[0]),
            obj1)

    def test_getLockingTID(self):
        uuid = self.getNewUUID()
        serial1, obj1 = self._getObject(1)
        oid1 = obj1[0]
        tid1, txn1 = self._getTransaction()
        self.assertEqual(self.manager.getLockingTID(oid1), None)
        self.manager.register(uuid, tid1)
        self.manager.storeObject(tid1, serial1, *obj1)
        self.assertEqual(self.manager.getLockingTID(oid1), tid1)

    def test_updateObjectDataForPack(self):
        ram_serial = self.getNextTID()
        oid = self.getOID(1)
        orig_serial = self.getNextTID()
        uuid = self.getNewUUID()
        locking_serial = self.getNextTID()
        other_serial = self.getNextTID()
        new_serial = self.getNextTID()
        compression = 1
        checksum = 42
        value = 'foo'
        self.manager.register(uuid, locking_serial)
        def getObjectData():
            return (compression, checksum, value)
        # Object not known, nothing happens
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), None)
        self.manager.updateObjectDataForPack(oid, orig_serial, None, None)
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), None)
        self.manager.abort(locking_serial, even_if_locked=True)
        # Object known, but doesn't point at orig_serial, it is not updated
        self.manager.register(uuid, locking_serial)
        self.manager.storeObject(locking_serial, ram_serial, oid, 0, 512,
            'bar', None)
        orig_object = self.manager.getObjectFromTransaction(locking_serial,
            oid)
        self.manager.updateObjectDataForPack(oid, orig_serial, None, None)
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), orig_object)
        self.manager.abort(locking_serial, even_if_locked=True)

        self.manager.register(uuid, locking_serial)
        self.manager.storeObject(locking_serial, ram_serial, oid, None, None,
            None, other_serial)
        orig_object = self.manager.getObjectFromTransaction(locking_serial,
            oid)
        self.manager.updateObjectDataForPack(oid, orig_serial, None, None)
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), orig_object)
        self.manager.abort(locking_serial, even_if_locked=True)
        # Object known and points at undone data it gets updated
        # ...with data_serial: getObjectData must not be called
        self.manager.register(uuid, locking_serial)
        self.manager.storeObject(locking_serial, ram_serial, oid, None, None,
            None, orig_serial)
        self.manager.updateObjectDataForPack(oid, orig_serial, new_serial,
            None)
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), (oid, None, None, None, new_serial))
        self.manager.abort(locking_serial, even_if_locked=True)
        # with data
        self.manager.register(uuid, locking_serial)
        self.manager.storeObject(locking_serial, ram_serial, oid, None, None,
            None, orig_serial)
        self.manager.updateObjectDataForPack(oid, orig_serial, None,
            getObjectData)
        self.assertEqual(self.manager.getObjectFromTransaction(locking_serial,
            oid), (oid, compression, checksum, value, None))
        self.manager.abort(locking_serial, even_if_locked=True)

if __name__ == "__main__":
    unittest.main()
