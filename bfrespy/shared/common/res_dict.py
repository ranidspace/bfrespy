from ..core import ResFileLoader, IResData
from .res_string import ResString
from abc import abstractmethod

# TODO a lot of modules needed for saving

class ResDict(IResData):
    """Represents the non-generic base of a dictionary which can quickly 
    look up IResData instances via key or index.
    """

    def __init__(self):
        self._nodes = []
    
    def __len__(self):
        return len(self._nodes) - 1
    
    # Operators
    
    def __getitem__(self, key):
        if type(key) is int or type(key) is str:
            node, index = self.__lookup(key)
            return node.value

        if type(key) is IResData:
            node, index = self.__lookup(key)
            return node.key
    
    def __setitem__(self, key, value):
        if type(key) is int:
            node = self.__lookup(key)
            node.value = value
        
        if type(key) is str:
            node, index = self.__lookup(key, False)
            if node:
                node.value = value
            else:
                self._nodes.append(self.Node(key, value))

        if type(key) is IResData:
            self.__lookup(key)
            node, index = self.__lookup(value)
            if node:
                raise ValueError(f"Key {value} already exists.")
    
    # Properties

    def keys(self):
        """Gets all keys under which instances are stored."""
        for node in self._nodes[1:]:
            yield node.key
    
    def values(self):
        """Gets all stored instances."""
        for node in self._nodes[1:]:
            yield node.value
    
    def nodes(self):
        """Returns only the publically visible nodes,
        excluding the root node.
        """
        for node in self._nodes[1:]:
            yield node
    
    # Public Methods

    def clear(self):
        """Removes all elements from the dictionary"""
        self._nodes.clear()
        self._nodes.append(self.Node())

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
    
    def index_of(self, key: str):
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

    def add(self, key, value):
        """Adds the given value under the specified key."""
        node, index = self.__lookup(key, False)
        if node:
            raise ValueError(f'Key "{key}" already exists.')
        self._nodes.append(self.Node(key,value))
        
    def contains_value(self, value: IResData):
        """Determines whether the given value is in the dictionary."""
        node, index = self.__lookup(value, False)
        if node:
            return True
        else:
            return False
        
    def index_of(self, value: IResData):
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
    
    def to_array(self) -> list[list[str, IResData]]:
        """Copies the elements of the dictionary as [key, value] instances to
        a new array and returns it.
        """
        res_data = [None] * len(self)
        for i, node in enumerate(self.nodes()):
            res_data = [node.key, node.value]
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

    def load(self, loader: ResFileLoader):
        loader.read_uint32()  # Always 0 on switch, total size on Wii U
        num_nodes = loader.read_uint32()  # Excluding Root node

        i = 0
        # Read the nodes including the root node.
        nodes = []
        while (num_nodes >= 0):
            nodes.append(self.__read_node(loader))
            i += 1  # XXX What does i do here?
            num_nodes -= 1
        self._nodes = nodes

    # Protected Methods

    @abstractmethod
    def _load_node_value(self, loader):
        """Loads an IResData instance from the given loader"""
        return

    # Private Methods
    
    def __read_node(self, loader: ResFileLoader):
        node = self.Node()

        node.reference = loader.read_uint32()
        node.idx_left = loader.read_uint16()
        node.idx_right = loader.read_uint16()
        node.key = loader.load_string()
        if (not loader.is_switch):
            node.value = loader._load_node_value(loader)
        return node
    
    def __lookup(self, key, throwonfail = True):
        if type(key) is int:
            if (key < 0 or key > len(self._nodes)):
                if (throwonfail):
                    raise IndexError(f"{key} out of bounds in {self}.")
                return None
            node = self._nodes[key+1]
            return node, key
        
        if type(key) is str:
            for i, found_node in enumerate(self.nodes()):
                if (found_node.key == key):
                    return found_node, i
            if (throwonfail):
                raise ValueError("{key} not found in {this}.")

        if type(key) is ResString:
            for i, found_node in enumerate(self.nodes()):
                if (type(found_node.value) is ResString):
                    if (str(found_node.value) == str(key)):
                        return found_node, i
        
        for i, found_node in enumerate(self.nodes()):
            if (found_node.value == key):
                return found_node, i
        if (throwonfail):
            raise ValueError("{key} not found in {this}.")
        return None, -1
    
    class Node:
        size_in_bytes = 16
        def __init__(self, key = None, value = None):
            self.reference = 0xFFFFFFFF
            self.idx_left: int
            self.idx_right: int
            self.key: str
            self.value: IResData
            if key and value:
                self.key = key
                self.value = value