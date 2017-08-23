import copy
import datrie
import string
from nltk.corpus import wordnet
from vocabulary.vocabulary import Vocabulary as vb

words = "/usr/share/dict/words"
dictionary = None


class Node:
    def __init__(self, x, y, value, grid, used):
        self.x = x
        self.y = y
        self.grid = grid
        self.used = used
        self.used.add(self)
        self.value = value

    def __hash__(self):
        return self.x ^ self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def getValue(self):
        return self.value

    def getNeighbors(self):
        neighbors = []
        prefix = self.getValue()

        if (self.x > 0):
            value = prefix + self.grid[self.y][self.x - 1]
            neighbors.append(Node(self.x - 1, self.y, value, self.grid, copy.copy(self.used)))
            if (self.y > 0):
                value = prefix + self.grid[self.y - 1][self.x - 1]
                neighbors.append(Node(self.x - 1, self.y - 1, value, self.grid, copy.copy(self.used)))
            if (self.y < len(self.grid) - 1):
                value = prefix + self.grid[self.y + 1][self.x - 1]
                neighbors.append(Node(self.x - 1, self.y + 1, value, self.grid, copy.copy(self.used)))
                
        if (self.y > 0):
            value = prefix + self.grid[self.y - 1][self.x]
            neighbors.append(Node(self.x, self.y - 1, value, self.grid, copy.copy(self.used)))
            
        if (self.x < len(self.grid[0]) - 1):
            value = prefix + self.grid[self.y][self.x + 1]
            neighbors.append(Node(self.x + 1, self.y, value, self.grid, copy.copy(self.used)))
            if (self.y > 0):
                value = prefix + self.grid[self.y - 1][self.x + 1]
                neighbors.append(Node(self.x + 1, self.y - 1, value, self.grid, copy.copy(self.used)))
            if (self.y < len(self.grid) - 1):
                value = prefix + self.grid[self.y + 1][self.x + 1]
                neighbors.append(Node(self.x + 1, self.y + 1, value, self.grid, copy.copy(self.used)))
                
        if (self.y < len(self.grid) - 1):
            value = prefix + self.grid[self.y + 1][self.x]
            neighbors.append(Node(self.x, self.y + 1, value, self.grid, copy.copy(self.used)))

        validNeighbors = []
        realWords = []
        for neighbor in neighbors:
            if neighbor not in self.used:
                key = neighbor.getValue()
                if (dictionary.has_keys_with_prefix(key)):
                    validNeighbors.append(neighbor)
                    if (key in dictionary and len(key) > 3):
                        realWords.append(key)
        
        return validNeighbors, realWords


class BoggleSolver:
    def __init__(self, grid, beThorough = False):
        self.grid = grid
        self.beThorough = beThorough
        self.initializeDictionary()

    def solveBoggle(self):
        gridWidth = len(self.grid[0])
        gridHeight = len(self.grid)
        queue = []

        # Initialize the queue with each of the boggle squares
        for y in range(gridHeight):
            for x in range(gridWidth):
                node = Node(x, y, self.grid[y][x], self.grid, set())
                queue.append(node)

        boggleWords = []
        while (queue):
            current = queue.pop(0)
            neighbors, realWords = current.getNeighbors()
            queue.extend(neighbors)
            boggleWords.extend(realWords)

        if (self.beThorough):
            boggleWords = self.validateWordsThoroughly(boggleWords)
        else:
            boggleWords = self.validateWordsQuickly(boggleWords)

        return boggleWords        

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

    def validateWordsQuickly(self, words):
        validWords = []
        for word in words:
            partOfSpeech = wordnet.synsets(word)
            if (partOfSpeech):
                validWords.append(word)
        return validWords

    def validateWordsThoroughly(self, words):
        validWords = []
        for word in words:
            partOfSpeech = vb.part_of_speech(word)
            if (partOfSpeech):
                validWords.append(word)
        return validWords


def main():
    boggleGrid = [
        ['n', 'e', 'y', 'r', 's'],
        ['i', 'k', 'a', 't', 'g'],
        ['e', 'p', 'w', 'n', 'e'],
        ['a', 'd', 'n', 't', 's'],
        ['l', 'n', 't', 'i', 'c']
    ]
    boggleSolver = BoggleSolver(boggleGrid, True)
    words = boggleSolver.solveBoggle()
    print(words)

main()
