import tempfile
import unittest
from datetime import date
from pathlib import Path
from database import (initialize, create_request, get_requests, update_status,
                      set_archived, add_inventory, get_inventory, adjust_inventory, seed_demo)

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'test.db'
        initialize(self.path)

    def tearDown(self):
        self.directory.cleanup()

    def test_request_approval_archive(self):
        rid = create_request('Test User','555','8 inch','Vanilla','Vanilla buttercream',
                             'Flowers',date(2027,1,1),'No nuts',self.path)
        self.assertEqual(get_requests(self.path)[0]['status'], 'Pending')
        update_status(rid, 'Approved', 'Looks good',self.path)
        set_archived(rid, True,self.path)
        self.assertEqual(get_requests(self.path)[0]['baker_note'], 'Looks good')
        self.assertEqual(get_requests(self.path)[0]['archived'], 1)
        set_archived(rid, False,self.path)
        self.assertEqual(get_requests(self.path)[0]['archived'], 0)

    def test_inventory_cannot_go_negative(self):
        add_inventory('Flour','Dry ingredients',2,3,'bags',self.path)
        item = get_inventory(self.path)[0]
        self.assertFalse(adjust_inventory(item['id'],-3,self.path))
        self.assertTrue(adjust_inventory(item['id'],1,self.path))
        self.assertEqual(get_inventory(self.path)[0]['quantity'],3)

    def test_seed_only_when_empty(self):
        seed_demo(self.path)
        seed_demo(self.path)
        self.assertEqual(len(get_requests(self.path)),2)
        self.assertEqual(len(get_inventory(self.path)),5)

if __name__ == '__main__':
    unittest.main()
