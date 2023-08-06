from datetime import datetime, timedelta
from unittest import TestCase, main

import cache
from datetimestub import DatetimeStub


class TestCache(TestCase):

    def setUp(self):
        super(TestCache, self).setUp()
        cache.datetime = DatetimeStub()     # Stub datetime to be able to mock datetime.now()
        self.cache = cache.Cache()

    def tearDown(self):
        self.cache.clear()
        cache.datetime = datetime
        super(TestCache, self).tearDown()

    def test_cache_set_without_timeout(self):
        """Setting item without timeout must be cached forever."""
        self.cache.set('superman', 'clark kent')
        self.cache.set('recipe', {'sugar': 2, 'wine': 5})

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})

        # Move time forward 10 years
        cache.datetime.now = lambda: datetime.now() + timedelta(days=10*365)

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})

    def test_cache_set_with_positive_timeout(self):
        """Setting item with positive timeout must be cached for the specified length of time (in seconds)."""
        self.cache.set('superman', 'clark kent', 5)
        self.cache.set('recipe', {'sugar': 2, 'wine': 5}, 10)

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})

        # Move time forward 5 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=5)

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})

        # Move time forward 10 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=10)

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)

    def test_cache_set_with_zero_or_negative_timeout(self):
        """Setting item with zero or negative timeout must not be cached."""
        self.cache.set('goner', 'to be expired')

        self.cache.set('superman', 'clark kent', 0)
        self.cache.set('recipe', {'sugar': 2, 'wine': 5}, -10)
        self.cache.set('goner', 'expired', 0)

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('goner'), None)

        # Move time forward 5 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=5)

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('goner'), None)

    def test_cache_get_non_existent_item(self):
        """Getting non-existent item must not throw exception."""
        self.assertEqual(self.cache.get('ghost'), None)
        self.assertEqual(self.cache.get('ghost', 'never exists'), 'never exists')

    def test_cache_get_with_default(self):
        """Getting expired or non-existent item with default value must return the default value."""
        self.cache.set('superman', 'clark kent', 5)
        self.cache.set('recipe', {'sugar': 2, 'wine': 5}, 10)
        self.cache.set('secret', ['remains secret'], 0)

        self.assertEqual(self.cache.get('superman', 'default'), 'clark kent')
        self.assertEqual(self.cache.get('recipe', {'default': True}), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('secret', ['default']), ['default'])
        self.assertEqual(self.cache.get('ghost', 0), 0)

        # Move time forward 5 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=5)

        self.assertEqual(self.cache.get('superman', 'default'), 'default')
        self.assertEqual(self.cache.get('recipe', {'default': True}), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('secret', ['default']), ['default'])
        self.assertEqual(self.cache.get('ghost', 0), 0)

        # Move time forward 10 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=10)

        self.assertEqual(self.cache.get('superman', 'default'), 'default')
        self.assertEqual(self.cache.get('recipe', {'default': True}), {'default': True})
        self.assertEqual(self.cache.get('secret', ['default']), ['default'])
        self.assertEqual(self.cache.get('ghost', 0), 0)

    def test_cache_add_without_timeout(self):
        """Adding item without timeout must be cached forever only if the item does not already exist."""
        self.cache.set('garbage', 'full')

        self.assertTrue(self.cache.add('superman', 'clark kent'))
        self.assertTrue(self.cache.add('recipe', {'sugar': 2, 'wine': 5}))
        self.assertFalse(self.cache.add('garbage', 'empty'))

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('garbage'), 'full')

        # Move time forward 10 years
        cache.datetime.now = lambda: datetime.now() + timedelta(days=10*365)

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('garbage'), 'full')

        # Try adding items again
        self.assertFalse(self.cache.add('superman', 'not kent'))
        self.assertFalse(self.cache.add('recipe', {'sugar': None, 'wine': 'A bottle'}))
        self.assertFalse(self.cache.add('garbage', 'empty'))

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('garbage'), 'full')

    def test_cache_add_with_positive_timeout(self):
        """
        Adding item without timeout must be must be cached for the specified length of time (in seconds) only if
        the item does not already exist.
        """
        self.cache.set('garbage', 'full', 10)

        self.assertTrue(self.cache.add('superman', 'clark kent', 10))
        self.assertTrue(self.cache.add('recipe', {'sugar': 2, 'wine': 5}, 20))
        self.assertFalse(self.cache.add('garbage', 'empty', 20))

        self.assertEqual(self.cache.get('superman'), 'clark kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('garbage'), 'full')

        # Move time forward 10 seconds
        cache.datetime.now = lambda: datetime.now() + timedelta(seconds=10)

        self.assertTrue(self.cache.add('superman', 'not kent', 10))
        self.assertFalse(self.cache.add('recipe', {'sugar': None, 'wine': 'A bottle'}, 10))
        self.assertTrue(self.cache.add('garbage', 'empty', 10))

        self.assertEqual(self.cache.get('superman'), 'not kent')
        self.assertEqual(self.cache.get('recipe'), {'sugar': 2, 'wine': 5})
        self.assertEqual(self.cache.get('garbage'), 'empty')

        # Move time forward 10 years
        cache.datetime.now = lambda: datetime.now() + timedelta(days=10*365)

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('garbage'), None)

    def test_cache_add_with_negative_timeout(self):
        """Adding item with zero or negative timeout must not be cached."""
        self.cache.set('garbage', 'full')

        self.assertFalse(self.cache.add('superman', 'clark kent', -10))
        self.assertFalse(self.cache.add('recipe', {'sugar': 2, 'wine': 5}, -20))
        self.assertFalse(self.cache.add('garbage', 'empty', -20))

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('garbage'), 'full')

    def test_cache_delete(self):
        """Deleting item must remove the item from cache."""
        self.cache.set('superman', 'clark kent')
        self.cache.set('recipe', {'sugar': 2, 'wine': 5}, 10)
        self.cache.set('secret', ['remains secret'], 0)

        self.cache.delete('superman')
        self.cache.delete('recipe')
        self.cache.delete('secret')
        self.cache.delete('ghost')

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('secret'), None)
        self.assertEqual(self.cache.get('ghost'), None)

    def test_cache_clear(self):
        """Clearing cache must empty the cache."""
        self.cache.set('superman', 'clark kent')
        self.cache.set('recipe', {'sugar': 2, 'wine': 5}, 10)
        self.cache.set('secret', ['remains secret'], 0)

        self.cache.clear()

        self.assertEqual(self.cache.get('superman'), None)
        self.assertEqual(self.cache.get('recipe'), None)
        self.assertEqual(self.cache.get('secret'), None)
        self.assertEqual(self.cache.get('ghost'), None)


if __name__ == '__main__':
    main()