from Products.Archetypes.utils import OrderedDict as BaseClass

class OrderedDict(BaseClass):
    """Container for a class with extra API for reordering, etc.
    Depreciated. I'll remove as soon as no classes having that class referenced"""
    
    def remove(self, hashKey=None, number=None):
        key = hashKey
        if not number is None:
            key = self._keys[number]
        BaseClass.__delitem__(self, key)

    def moveDown(self, number=None, hashKey=None):
        """
        Moving down the screen means moving up the list
        If no argument provided I move up the first element
        """
        keys = self._keys
        if number is None:
            if hashKey is None:
                number = 0
            else:
                if hashKey in keys:
                    number = keys.index(hashKey)
                else:
                    return
        if number<len(keys)-1:
            keys[number], keys[number+1] = keys[number+1], keys[number]

    def moveUp(self, number=None, hashKey=None):
        """
        Moving up the screen means moving down the list
        If no argument provided I move down the last element
        """
        keys = self._keys
        if number is None:
            if hashKey is None:
                number = len(keys)-1
            else:
                if hashKey in keys:
                    number = keys.index(hashKey)
                else:
                    return
        if number:
            keys[number], keys[number-1] = keys[number-1], keys[number]
