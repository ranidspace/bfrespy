from ..core import ResFileLoader, IResData
from .res_string import ResString
from typing import TypeVar, Generic, overload
from collections.abc import Iterator, Collection

T = TypeVar('T', bound=IResData)


class Node(Generic[T]):
    size_in_bytes = 16

    def __init__(self, key=None, value=None):
        self.reference = 0xFFFFFFFF
        self.idx_left: int
        self.idx_right: int
        self.key: str
        self.value: T
        if key and value:
            self.key = key
            self.value = value

    def __repr__(self) -> str:
        return f"ResDictNode('{self.key}': '{self.value}')"


class ResDict(IResData, Collection[Node[T]]):
    """Represents the non-generic base of a dictionary which can quickly
    look up IResData instances via key or index.
    """

    def __init__(self):
        self._nodes: list[Node[T]] = [Node()]

    def __len__(self):
        return len(self._nodes) - 1

    def __iter__(self):
        for node in self.nodes():
            yield (node.key, node.value)

    def __repr__(self):
        return (
            'ResDict{'
            + ', '.join([f'{node.key}: {node.value}' for node in self.nodes()])
            + '}'
        )

    def __contains__(self, x: object) -> bool:
        node, index = self.__lookup(x, False)
        if node:
            return True
        else:
            return False

    # Operators

    @overload
    def __getitem__(self, key: int | str) -> T: ...

    @overload
    def __getitem__(self, key: IResData) -> str: ...

    def __getitem__(self, key):
        if isinstance(key, int | str):
            node, index = self.__lookup(key)
            return node.value

        if isinstance(key, IResData):
            node, index = self.__lookup(key)
            return node.key

    def __setitem__(self, key, value: T):
        if isinstance(key, int):
            node, index = self.__lookup(key)
            node.value = value

        if isinstance(key, str):
            node, index = self.__lookup(key, False)
            if node:
                node.value = value
            else:
                self._nodes.append(Node(key, value))

        if isinstance(key, IResData):
            self.__lookup(key)
            node, index = self.__lookup(value)
            if node:
                raise ValueError(f"Key {value} already exists.")

    # Properties

    def keys(self) -> Iterator[str]:
        """Gets all keys under which instances are stored."""
        for node in self._nodes[1:]:
            yield node.key

    def values(self) -> Iterator[T]:
        """Gets all stored instances."""
        for node in self._nodes[1:]:
            yield node.value

    def nodes(self) -> Iterator[Node[T]]:
        """Returns only the publically visible nodes,
        excluding the root node.
        """
        for node in self._nodes[1:]:
            yield node

    def items(self):
        for node in self._nodes[1:]:
            yield (node.key, node.value)

    # Public Methods

    def clear(self):
        """Removes all elements from the dictionary"""
        self._nodes.clear()
        self._nodes.append(Node())

    def contains_key(self, key):
        """Determines whether an instance is saved
        under the given key in the dictionary.
        """
        node, index = self.__lookup(key, False)

    def get_key(self, index: int):
        """Returns they key of a given index"""
        node, idx = self.__lookup(index, True)  # XXX Shouldn't this be false?
        if node:
            return node.key
        return ""

    def index_of_key(self, key: str):
        """Searches for the specified key and returns the zero-based
        index of the first occurrence within the entire dictionary.
        """
        node, index = self.__lookup(key, False)
        return (index if node else -1)

    def rename(self, key, new_key):
        """Changes the key of the instance currently saved under the
        given key to the new_key
        """
        # Throw if key doesnt exist
        node, index = self.__lookup(key)
        # Throw if new key already exists
        existingnode, index = self.__lookup(key, False)
        if (existingnode):
            raise ValueError(f'Key "{new_key}" already exists.')

    def remove_key(self, key):
        """Removes the first occurrence of the instance with the
        specific key from the dictionary.
        """
        node, index = self.__lookup(key, False)
        if node:
            self._nodes.remove(node)
            return True
        else:
            return False

    def remove_at(self, index):
        """Removes the instance at the specified index of the dictionary."""
        node, idx = self.__lookup(index, True)
        self._nodes.remove(node)

    def try_get_value(self, key):
        node, index = self.__lookup(key, False)
        if node:
            return node.value
        else:
            return None

    # Internal Methods

    def append(self, key, value):
        """Adds the given value under the specified key."""
        node, index = self.__lookup(key, False)
        if node:
            raise ValueError(f'Key "{key}" already exists.')
        self._nodes.append(Node(key, value))

    def index_of_value(self, value: IResData):
        """Searches for the specified value and returns the zero-based
        index of the first occurrence within the entire dictionary."""
        node, index = self.__lookup(value, False)
        if node:
            return index
        else:
            return -1

    def remove(self, value: IResData):
        """Removes the first occurrence of a specific value
        from the dictionary."""
        node, index = self.__lookup(value, False)
        if node:
            self._nodes.remove(node)
            return True
        else:
            return False

    def to_dict(self) -> dict[str, T]:
        """Copies the elements of the dictionary to a python dict
        """
        res_data = {}
        for i, node in enumerate(self.nodes()):
            res_data[node.key] = node.value
        return res_data

    def try_get_key(self, value):
        """Returns True if a key was found for the given value and has been
        assigned to key, or None if no key was found.
        """
        node, index = self.__lookup(value, False)
        if node:
            return node.key
        else:
            return None

    # Methods

    def load(self, T: type[IResData], loader: ResFileLoader):
        loader.read_uint32()  # Always 0 on switch, total size on Wii U
        num_nodes = loader.read_uint32()  # Excluding Root node

        i = 0
        # Read the nodes including the root node.
        nodes = []
        while (num_nodes >= 0):
            nodes.append(self.__read_node(T, loader))
            i += 1  # XXX What does i do here?
            num_nodes -= 1
        self._nodes = nodes

    # Protected Methods

    def _load_node_value(self, T, loader):
        """Loads an IResData instance from the given loader"""
        return loader.load(T)

    # Private Methods

    def __read_node(self, T, loader: ResFileLoader) -> Node:
        node = Node()

        node.reference = loader.read_uint32()
        node.idx_left = loader.read_uint16()
        node.idx_right = loader.read_uint16()
        node.key = loader.load_string()
        if (not loader.is_switch):
            node.value = self._load_node_value(T, loader)
        return node

    def __lookup(self, key, throwonfail=True) -> tuple[Node, int]:
        if isinstance(key, int):
            if (key < 0 or key > len(self._nodes)):
                if (throwonfail):
                    raise IndexError(f"{key} out of bounds in {self}.")
                return (None, -1)  # type: ignore
            node = self._nodes[key + 1]
            return (node, key)

        elif isinstance(key, str):
            for i, found_node in enumerate(self.nodes()):
                if (found_node.key == key):
                    return (found_node, i)
            if (throwonfail):
                raise ValueError("{key} not found in {this}.")
            return (None, -1)  # type: ignore

        # The next two lookup by value, not key.
        elif isinstance(key, ResString):
            for i, found_node in enumerate(self.nodes()):
                if (isinstance(found_node.value, ResString)):
                    if (str(found_node.value) == str(key)):
                        return (found_node, i)

        else:
            for i, found_node in enumerate(self.nodes()):
                if (found_node.value == key):
                    return (found_node, i)
            if (throwonfail):
                raise ValueError("{key} not found in {this}.")
            return (None, -1)  # type: ignore
