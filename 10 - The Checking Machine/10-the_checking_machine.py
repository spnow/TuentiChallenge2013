#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tuenti Challenge 3
#
# Challenge 10 - The Checking Machine

# C-3PO: I am fluent in over six million forms of communication

import sys
import md5
import re

''' Tree structure:
    Each node is a list with 3 items:
    [ count, own_len, elements ]
    
    count: Number of times the result of this node has to be repeated
    own_len: Length of the strings contained only in this node (not in its children)
    elements: List of strings or subtrees in order
'''


def calculate_hash(tree, m):
    for i in xrange(tree[0]):
        for elem in tree[2]:
            if isinstance(elem, list):
                calculate_hash(elem, m)
            else:
                m.update(elem)

                        
def create_tree(tree, tokens):
    ''' Parses the tokens to contruct the tree structure '''
    own_len = 0
    
    while len(tokens):
        token = tokens[0]
        del tokens[0]
        
        if isinstance(token, int) or token == '[':
            if isinstance(token, int):
                del tokens[0]
                node = [token, 0, []]
            else:
                node = [1, 0, []]
            
            create_tree(node, tokens)
            tree[2].append(node)
            
        elif token == ']':
            return
        else:
            own_len += len(token)
            tree[2].append(token)
            
        tree[1] = own_len
        

def get_tree_length(tree):
    ''' Get the length of the string generated by the tree/subtree. '''
    l = 0    
    for elem in tree[2]:
        if isinstance(elem, list):
            l += get_tree_length(elem)

    return (l * tree[0]) + (tree[0] * tree[1])



def generate_string(tree):
    ''' Generate the full string specified by the tree/subtree '''
    s = ""
    
    for elem in tree[2]:
        if isinstance(elem, list):
            s += generate_string(elem)
        else:
            s += elem            
    return s * tree[0]


def optimize_tree(tree, max_limit):
        ''' Optimizes a tree. It tries to collapse all the possible subtrees using
            bigger buffers. The max_limit parameter specifies which is the maximum
            buffer allowed. All the subtrees that fit in this size, will be pre-generated
            and stored in the tree.
            
            This allows faster MD5 calculation
        '''
        own_total_length = tree[0] * tree[1]
        
        for i in range(len(tree[2])):
            elem = tree[2][i]
            if isinstance(elem, list):
                subtree_length = get_tree_length(elem)
                if subtree_length + own_total_length <= max_limit:
                    # Pre-generate the string and overwrite the element
                    s = generate_string(elem)
                    tree[2][i] = s
                    tree[1] += len(s)
                    max_limit -= len(s)
                else:
                    optimize_tree(elem, max_limit - own_total_length)
                    
        # For extra points, join adjacent strings
        i = 0
        while i < len(tree[2]) - 1:
            if not isinstance(tree[2][i], list) and not isinstance(tree[2][i + 1], list):
                s = tree[2][i] + tree[2][i + 1]
                tree[2][i] = s
                del tree[2][i + 1]
            else:
                i += 1
        

if __name__ == '__main__':
    
    tokenizer = re.compile(r'[a-zA-Z]+|[0-9]+|\[|\]')
    is_integer = re.compile(r'^[0-9]+$')    
    
    for line in sys.stdin:
        line = line.rstrip('\r\n')
        
        m = md5.new()
        tokens = []        
        for token in tokenizer.findall(line):
            if is_integer.match(token):
                tokens.append(int(token))
            else:
                tokens.append(token)

        tree = [1,0, []]
        create_tree(tree, tokens)
        # Use up to 100MB of RAM to optimize the tree
        optimize_tree(tree, 100 * 1024 * 1024)
        calculate_hash(tree, m)
        print m.hexdigest()

