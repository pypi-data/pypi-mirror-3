from helpers import RepoTestCase

import jsongit

class TestLog(RepoTestCase):

    def test_no_log(self):
        """Starts with just the most recent step.
        """
        self.repo.commit('fresh', {'foo': 'bar'})
        gen = self.repo.log('fresh')
        commit = gen.next()
        self.assertEquals(commit, self.repo.head('fresh'))
        self.assertEquals(commit.data, self.repo.head('fresh').data)

    def test_default_log(self):
        """Should step through commits backwards all the way by default.
        """
        self.repo.commit('foo', 'step 1')
        self.repo.commit('foo', 'step 2')
        self.repo.commit('foo', 'step 3')
        self.repo.commit('foo', 'step 4')

        gen = self.repo.log('foo')

        self.assertEquals('step 4', gen.next().data)
        self.assertEquals('step 3', gen.next().data)
        self.assertEquals('step 2', gen.next().data)
        self.assertEquals('step 1', gen.next().data)
        with self.assertRaises(StopIteration):
            gen.next()

    def test_reverse_log(self):
        """Can specify a reverse log.
        """
        self.repo.commit('foo', 'step 1')
        self.repo.commit('foo', 'step 2')
        self.repo.commit('foo', 'step 3')
        self.repo.commit('foo', 'step 4')

        gen = self.repo.log('foo', order=jsongit.GIT_SORT_REVERSE)

        self.assertEquals('step 1', gen.next().data)
        self.assertEquals('step 2', gen.next().data)
        self.assertEquals('step 3', gen.next().data)
        self.assertEquals('step 4', gen.next().data)
        with self.assertRaises(StopIteration):
            gen.next()

    def test_log_messages(self):
        """Retrieves log messages.
        """
        self.repo.commit('foo', 'bar', message="I think this is right.")
        self.repo.commit('foo', 'baz', message="Nope, it was wrong.")

        gen = self.repo.log('foo')

        self.assertEquals("Nope, it was wrong.", gen.next().message)
        self.assertEquals("I think this is right.", gen.next().message)

    def test_log_authors(self):
        """Retrieves authors.
        """
        bob = jsongit.utils.signature('bob', 'bob@bob.com')
        dan = jsongit.utils.signature('dan', 'dan@dan.com')
        self.repo.commit('foo', 'bar', author=bob)
        self.repo.commit('foo', 'baz', author=dan)

        gen = self.repo.log('foo')

        c = gen.next()
        self.assertEquals("dan", c.author.name)
        self.assertEquals("dan@dan.com", c.author.email)
        c = gen.next()
        self.assertEquals("bob", c.author.name)
        self.assertEquals("bob@bob.com", c.author.email)

    def test_merge_log(self):
        """Provides history for merged data that includes all parents.

        Changes should be registered at point they are merged.
        """
        self.repo.commit('foo', {'roses': 'red'})
        self.repo.checkout('foo', 'bar')
        self.repo.commit('foo', {'roses': 'red', 'violets': 'blue'})
        self.repo.commit('bar', {'roses': 'red', 'lilacs': 'purple'})
        merge = self.repo.merge('bar', 'foo')
        self.assertTrue(merge.success)

        gen = self.repo.log('bar')

        self.assertEquals({'roses': 'red', 'violets':'blue', 'lilacs':'purple'},
                          gen.next().data)
        self.assertEquals({'roses': 'red', 'violets':'blue'},
                          gen.next().data,
                         "Merge occurred after modification to bar.")
        self.assertEquals({'roses': 'red', 'lilacs':'purple'},
                          gen.next().data)
        self.assertEquals({'roses': 'red'}, gen.next().data)
        self.assertEquals({'roses': 'red'}, gen.next().data)
        with self.assertRaises(StopIteration):
            gen.next()

