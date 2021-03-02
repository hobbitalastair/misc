""" Trie implementation, for data structure revision """

class Trie:
    """ Recursive Trie implementation """

    def __init__(self):
        self.nodes = {}
        self.has_value = None
        self.value = None

    def __getitem__(self, key):
        """ Retrieve the value corresponding to the given key.
            
            See __setitem__ for test cases.
        """

        if len(key) == 0:
            if self.has_value:
                return self.value
            else:
                raise KeyError(key)
        else:
            try:
                subtrie = self.nodes[key[0]]
                return subtrie[key[1:]]
            except KeyError as e:
                raise KeyError(key)

    def __setitem__(self, key, value):
        """ Set the key/value pair in the Trie.
        >>> t = Trie()
        >>> key = "some test string"
        >>> t[key] = 100
        >>> t[key]
        100
        >>> t[""] = 1
        >>> t[""]
        1
        >>> t[key]
        100
        >>> t[key[:3]] = 2
        >>> t[key[:3]]
        2
        """
        if len(key) == 0:
            self.has_value = True
            self.value = value
        else:
            subtrie = self.nodes.get(key[0], Trie())
            self.nodes[key[0]] = subtrie
            subtrie[key[1:]] = value

    def __delitem__(self, key):
        """ Delete the given key from the trie.
        >>> t = Trie()
        >>> key = "test"
        >>> t[key] = 1
        >>> t[key]
        1
        >>> del t[key]
        >>> t[key]
        Traceback (most recent call last):
        KeyError: 'test'
        >>> del t["never existed"]
        Traceback (most recent call last):
        KeyError: 'never existed'
        >>> del t[""]
        Traceback (most recent call last):
        KeyError: ''
        """
        if len(key) == 0:
            if self.has_value:
                self.has_value = False
                self.value = None
            else:
                raise KeyError(key)
        else:
            # FIXME: We don't clean up hanging nodes here...
            try:
                subtrie = self.nodes[key[0]]
                del subtrie[key[1:]]
            except KeyError:
                raise KeyError(key)

    def __contains__(self, key):
        """
        >>> t = Trie()
        >>> key = "some test string"
        >>> t[key] = 100
        >>> key in t
        True
        >>> "not in t" in t
        False
        >>> "" in t
        False
        >>> key[:4] in t
        False
        """
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __iter__(self):
        """
        >>> t = Trie()
        >>> t["test 1"] = 1
        >>> t["test 2"] = 2
        >>> t["test 3a"] = 3
        >>> t["test"] = 4
        >>> for k in sorted(list(t)): print(k)
        test
        test 1
        test 2
        test 3a
        >>> t[""] = 5
        >>> for k in sorted(list(t)): print(":" + k)
        :
        :test
        :test 1
        :test 2
        :test 3a

        """
        if self.has_value:
            yield ''
        
        for k, v in self.nodes.items():
            for subkey in v:
                yield k + subkey
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
