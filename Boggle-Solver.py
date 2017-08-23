"""
Boggle-Solver.py

Author: Julia Edwards
Date: August, 2017
Github: jedwardsjunior
"""

import copy
import datrie
import string
from nltk.corpus import wordnet
from vocabulary.vocabulary import Vocabulary as vb

# Location of the built-in dictionary on a Mac
words = "/usr/share/dict/words"
dictionary = None

"""
validateWordQuickly()
    
Use the NLTK wordnet library to check whether the given word is a real word.

Inputs:
(string) word - the word to validate

Output:
(boolean) - whether or not this is a valid word
"""
def validateWordQuickly(word):
    partOfSpeech = wordnet.synsets(word)
    # Hack: If a part of speech was found, then we know this is a valid word.
    # TODO - add a check here to remove words that invalid by my family's
    #        rules (i.e. proper nouns)
    if (partOfSpeech):
        return True
        
    return False

"""
validateWordThoroughly()
    
Use the Python Vocabulary library to check whether the given word is a real word.
Note: requires an Internet connection to look up the words, and takes substantially
longer than validateWordQuickly() because of this. However, it does return more
words than validateWordQuickly().

Inputs:
(string) word - the word to validate

Output:
(boolean) - whether or not this is a valid word
"""
def validateWordThoroughly(word):
    partOfSpeech = vb.part_of_speech(word)
    # Hack: If a part of speech was found, then we know this is a valid word.
    # TODO - add a check here to remove words that invalid by my family's
    #        rules (i.e. proper nouns)
    if (partOfSpeech):
        return True
        
    return False


"""
class Node

Represents a prefix that can be made using distinct, connected squares from the
Boggle board.
"""
class Node:
    """
    Constructor for the Node class.

    Input:
    (Object) self - the object that this method is operating on
    (int) x - the y coordinate of this square in the Boggle grid
    (int) y - the y coordinate of this square in the Boggle grid
    (string) value - the prefix associated with this Node
    (int[][]) grid - the Boggle grid
    (Node[]) used - the list of Nodes already used to make the given value
    
    Output:
    (void)
    """
    def __init__(self, x, y, value, grid, used):
        self.x = x
        self.y = y
        self.grid = grid
        self.used = used
        self.used.add(self)
        self.value = value

    """
    Hash

    Two Nodes should have the same hash if they have the same x and y
    coordinate in the Boggle grid.

    Input:
    (Object) self - the object that this method is operating on

    Output:
    (int) - the hash for this object
    """
    def __hash__(self):
        return self.x ^ self.y

    """
    Equals

    Two Nodes are equal if they have the same x and y coordinate in the
    Boggle grid.

    Input:
    (Object) self - the object that this method is operating on

    Output:
    (boolean) - whether these two objects are equal to one another
    """
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    """
    getValue()

    Getter for the value stored in self.value.

    Input:
    (Object) self - the object that this method is operating on

    Output:
    (string) - the value stored in self.value
    """
    def getValue(self):
        return self.value

    """
    getNeighbors()

    Finds all valid neighbors - the neighbor can be used to make a valid prefix
    from distinct Boggle squares - and all real words that can be made using
    those valid neighbors.

    Inputs:
    (Object) self - the object that this method is operating on
    (boolean) beThorough - used to determine whether to validate
                           words with NLTK wordnet vs the Python Vocabulary
                           library. Default - False - uses NLTK wordnet.

    Outputs:
    (string[]) - a list of neighbor Nodes that should also be explored
    (string[]) - a list of the valid words that the neighbors can make
    """
    def getNeighbors(self, beThorough):
        neighbors = []
        prefix = self.getValue()

        # Explore the western neighbors
        if (self.x > 0):
            value = prefix + self.grid[self.y][self.x - 1]
            neighbors.append(Node(self.x - 1, self.y, value, self.grid, copy.copy(self.used)))

            # Northwest neighbor
            if (self.y > 0):
                value = prefix + self.grid[self.y - 1][self.x - 1]
                neighbors.append(Node(self.x - 1, self.y - 1, value, self.grid, copy.copy(self.used)))

            # Southwest neighbor
            if (self.y < len(self.grid) - 1):
                value = prefix + self.grid[self.y + 1][self.x - 1]
                neighbors.append(Node(self.x - 1, self.y + 1, value, self.grid, copy.copy(self.used)))

        # Explore the northern neighbor               
        if (self.y > 0):
            value = prefix + self.grid[self.y - 1][self.x]
            neighbors.append(Node(self.x, self.y - 1, value, self.grid, copy.copy(self.used)))

        # Explore the eastern neighbors           
        if (self.x < len(self.grid[0]) - 1):
            value = prefix + self.grid[self.y][self.x + 1]
            neighbors.append(Node(self.x + 1, self.y, value, self.grid, copy.copy(self.used)))

            # Northeast neighbor
            if (self.y > 0):
                value = prefix + self.grid[self.y - 1][self.x + 1]
                neighbors.append(Node(self.x + 1, self.y - 1, value, self.grid, copy.copy(self.used)))

            # Southest neighbor
            if (self.y < len(self.grid) - 1):
                value = prefix + self.grid[self.y + 1][self.x + 1]
                neighbors.append(Node(self.x + 1, self.y + 1, value, self.grid, copy.copy(self.used)))

        # Explore the southern neighbor              
        if (self.y < len(self.grid) - 1):
            value = prefix + self.grid[self.y + 1][self.x]
            neighbors.append(Node(self.x, self.y + 1, value, self.grid, copy.copy(self.used)))

        validNeighbors = []
        realWords = []
        for neighbor in neighbors:
            # Verify that the neighbor has not already been used in making the
            # current prefix
            if neighbor not in self.used:
                key = neighbor.getValue()
                # If the current prefix + the value of this neighbor is also a
                # valid prefix, add it to validNeighbors so we can explore
                # it later
                if (dictionary.has_keys_with_prefix(key)):
                    validNeighbors.append(neighbor)

                    # If this is word contains 4 or more letters, look up
                    # whether or not it is a valid word
                    if (len(key) > 3):
                        if (beThorough):
                            validWord = validateWordThoroughly(key)
                        else:
                            validWord = validateWordQuickly(key)
                            
                        # Found a valid word! Add it to realWords.
                        if (validWord):
                            realWords.append(key)
        
        return validNeighbors, realWords

"""
class BoggleSolver

Given a Boggle grid as input, utilizes the Node class to keep track of the
various 4+ letter words that can be made from distinct, connected squares in the
Boggle grid.
"""
class BoggleSolver:
    """
    Constructor for BoggleSolver

    Inputs:
    (Object) self - the object that this method is operating on
    (int[][]) grid - the Boggle grid

    Output:
    (void)
    """
    def __init__(self, grid):
        self.grid = grid
        self.initializeDictionary()

    """
    solveBoggle()

    Finds all the 4+ letter words in the Boggle grid by iterating through
    all the valid Nodes - each one representing a prefix found in the prefix
    tree created via initializedDictionary() - that can be made in this board.

    Inputs:
    (Object) self - the object that this method is operating on
    (boolean) beThorough - optional flag used to determine whether to validate
                           words with NLTK wordnet vs the Python Vocabulary
                           library. Default - False - uses NLTK wordnet.

    Output:
    (list) - a list of valid words found in this Boggle grid.
    """
    def solveBoggle(self, beThorough = False):
        gridWidth = len(self.grid[0])
        gridHeight = len(self.grid)

        # Keep track of the Nodes to explore in a queue
        queue = []
        # Initialize the queue with each of the boggle squares
        for y in range(gridHeight):
            for x in range(gridWidth):
                node = Node(x, y, self.grid[y][x], self.grid, set())
                queue.append(node)

        # Keep track of the valid words
        boggleWords = []
        while (queue):
            current = queue.pop(0)
            neighbors, realWords = current.getNeighbors(beThorough)
            queue.extend(neighbors)
            boggleWords.extend(realWords)

        return boggleWords        

    """
    initializeDictionary()

    Attempts to load a prefix Trie located at englishDictionary.trie (default
    implementation - feel free to store it wherever you want as whatever name
    you want). If the Trie cannot be loaded, creates a new one using the Python
    datrie library and the list of words that the "words" global variable is
    pointing to. Default implementation is to save the Trie so we only have to
    create it once.

    Input:
    (Object) self - the object that this method is operating on

    Output:
    (void)
    """
    def initializeDictionary(self):
        global dictionary
        try:
            dictionary = datrie.Trie.load('englishDictionary.trie')
            if (dictionary):
                 return
        except Exception:
            pass
    
        dictionary = datrie.Trie(string.ascii_lowercase)
        for word in open(words):
            dictionary[word.strip().lower()] = len(word)
        
        dictionary.save('englishDictionary.trie')



def main():
    # Sample Boggle grid
    boggleGrid = [
        ['n', 'e', 'y', 'r', 's'],
        ['i', 'k', 'a', 't', 'g'],
        ['e', 'p', 'w', 'n', 'e'],
        ['a', 'd', 'n', 't', 's'],
        ['l', 'n', 't', 'i', 'c']
    ]
    
    boggleSolver = BoggleSolver(boggleGrid)
    words = boggleSolver.solveBoggle()
    print(words)

main()
