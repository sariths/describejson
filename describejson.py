

_typeToString = {
    bool: 'boolean',
    dict: 'dict',
    float: 'float',
    int: 'int',
    list: 'list',
    int: 'int',
    type(None): 'None',
    str: 'str',
}


class JsonItem(object):
    """
    Typical usage:
        import json
        with open("somefile.json") as jsonData:
            jsonObj = json.load(jsonData)
            x = JsonItem(jsonObj, strictness="keys")
            print(x)

    """
    DEFAULT_STRICTNESS = 'length'

    def __init__(self, item, indent=0, strictness=None):
        """
        :param item: This is the item that is obtained after reading the json file and
            extracting the data from it.
        :param indent: The starting string indent.
        :param strictness: The option to determine how strictly JSON objects and lists should be compared.
            Strictness affects the amount of output you'll see. For example if a list contains two lists,
            `describejson.py` will just tell you that very concisely if you use `--strictness type`.
            If you want the fact that things differ in length or contents, use a higher strictness level.
            In order of increasing strictness, the possible values are:
                type- compare everything by type only.
                length- compare lists and objects by length.
                keys- compare lists by equality, objects by keys.
                equal- compare objects and list by equality.


        """
        self._strictness = strictness or self.DEFAULT_STRICTNESS
        self._compare = getattr(self, '_eq_%s' % self._strictness)
        self._indent = indent
        self._duplications = 1
        self._type = type(item)
        if self._type == dict:
            self._len = len(item)
            if strictness == 'keys':
                self._keys = sorted(item.keys())
            elif strictness == 'equal':
                self._item = item
            self._summarize(item.values())
        elif self._type == list:
            self._len = len(item)
            if strictness in ('keys', 'equal'):
                self._item = item
            self._summarize(item)

    def _summarize(self, items):
        self._contents = []
        for i, item in enumerate(items):
            jsonItem = JsonItem(item, self._indent + 2, self._strictness)
            if i == 0:
                self._contents.append(jsonItem)
            else:
                if self._contents[-1] == jsonItem:
                    self._contents[-1]._duplications += 1
                else:
                    self._contents.append(jsonItem)

    def __eq__(self, other):
        return self._compare(other)

    def _eq_type(self, other):
        """Equality only according to item type."""
        return self._type == other._type

    def _eq_length(self, other):
        """Dicts and lists must have the same number of keys."""
        if self._type == other._type:
            if self._type == dict or self._type == list:
                return self._len == other._len
            else:
                return True
        else:
            return False

    def _eq_keys(self, other):
        """Lists must be equal, dicts must have the same keys."""
        if self._type == other._type:
            if self._type == list:
                return self._item == other._item
            elif self._type == dict:
                return self._keys == other._keys
            else:
                return True
        else:
            return False

    def _eq_equal(self, other):
        """Lists and dicts must be equal."""
        if self._type == other._type:
            if self._type in (dict, list):
                return self._item == other._item
            else:
                return True
        else:
            return False

    def _strList(self):
        prefix = '%s%s %s%s' % (
            self._indent * ' ', self._duplications, _typeToString[self._type],
            '' if self._duplications == 1 else 's')
        if self._type in (dict, list):
            result = ['%s of length %d.%s' % (
                prefix, self._len, ' Values:' if self._len else '')]
            for item in self._contents:
                result.extend(item._strList())
        else:
            result = [prefix]
        return result

    def __str__(self):
        return '\n'.join(self._strList())


if __name__ == '__main__':
    pass