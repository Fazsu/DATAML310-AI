import argparse

import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | VP | S Conj S | S P S
NP -> N | Det N | Det NP | P NP | Adj NP | Adv NP | Conj NP | N NP | N Adv
VP -> V | V NP | Adv VP | V Adv
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('directory', help="load the data files from this directory", nargs="?")
    arg_parser.add_argument("-q", "--quiet", help="print just the noun phrase chunks (used by the grader)",
                            action="store_true")
    args = arg_parser.parse_args()

    # If filename specified, read sentence from file
    if args.directory is not None:
        with open(args.directory) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    if not args.quiet:
        #for tree in trees:
        tree = trees[0]
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))

    # Print just the noun phrase chunks
    else:
        np_set = set()
        #for tree in trees:
        tree = trees[0]
        for np in np_chunk(tree):
            np_set.add(" ".join(np.flatten()))

        print("Noun Phrase Chunks")
        for np in sorted(np_set):
            print(np)


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # get each word, different punctuations and any special characters that might arise
    # create them as a list
    tokens = nltk.word_tokenize(sentence)
    words = []

    for word in tokens:

        valid = False
        for letter in word:

            # if even one of the letters is an alphabet the element is a word
            # -> No special character or punctuation
            if letter.isalpha():
                valid = True

        # add all words to list of words, in lowercase
        if valid:
            word = word.lower()
            words.append(word)

    return words

def check_if_contains(branch):    
    # if branch (subtree) is an NP, True
    if branch.label() == "NP":
        return True
    
    # if the subtree has only one child, then its probably a terminal node
    # in which case return False
    # but the label must not be 'S' since
    # S can contain only one child when S -> VP is followed by the parse tree
    if len(branch) == 1 and branch.label() != 'S':
        return False 

    # Check further into elements in the branch (subtree)
    # and check each subsubbranch there
    for subsubtree in branch:

        if check_if_contains(subsubtree):
            return True

    return False


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunks = []

    for branch in tree:

        # get the label of the subtree defined by the grammar
        node = branch.label()
        
        # check if this tree contains a subtree with 'NP'
        # if not check another subtree
        contains = check_if_contains(branch)
        if not contains:
            continue
        
        # if the node is a NP or VP or S, then
        # go further into the tree to check for noun phrase chunks
        # at each point take the list of trees returned and
        # append each to the actual chunks' list in the parent
        if node == "NP" or node == "VP" or node == "S":
            subBranch = np_chunk(branch)
            for np in subBranch:
                np_chunks.append(np)

    # if the current tree has no subtree with a 'NP' label
    # and is itself an 'NP' labeled node then, append the tree to chunks
    if tree.label() == "NP" and not contains:
        np_chunks.append(tree)

    return np_chunks
    

if __name__ == "__main__":
    main()
