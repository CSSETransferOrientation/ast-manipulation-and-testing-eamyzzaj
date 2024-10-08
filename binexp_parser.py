#!/usr/bin/python3
import os
from os.path import join as osjoin

import unittest

from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator'])

class BinOpAst():
    """
    A somewhat quick and dirty structure to represent a binary operator AST.

    Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    """
    def __init__(self, prefix_list):
        """
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        """
        self.val = prefix_list.pop(0)
        if self.val.isnumeric():
            self.type = NodeType.number
            self.left = False
            self.right = False
        else:
            self.type = NodeType.operator
            self.left = BinOpAst(prefix_list)
            self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Convert the binary tree printable string where indentation level indicates
        parent/child relationships
        """
        ilvl = '  '*indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '\n  ' + ilvl + self.right.__str__(indent+1) if self.right else ''
        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        """Generate the repr from the string"""
        return str(self)

    def prefix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.val + ' ' + self.left.prefix_str() + ' ' + self.right.prefix_str()

    def infix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return '(' + self.left.infix_str() + ' ' + self.val + ' ' + self.right.infix_str() + ')'
    def postfix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.left.postfix_str() + ' ' + self.right.postfix_str() + ' ' + self.val


    # REQUIRED IMPLEMENTS
    def additive_identity(self):
        """
        Reduce additive identities
        x + 0 = x
        """
        # IMPLEMENTED
        #if it sees a zero is being added, should be just the number
        # ;;> You always want to do the recursive call to handle things like '* 10 + 1 0', see the propogate test I added
        if self.type == NodeType.operator and self.val == '+':
            self.left.additive_identity()
            self.right.additive_identity()

            #zero on left
            if self.left.type == NodeType.number and self.left.val == '0':
                #return self.right
                self.val = self.right.val
                self.type = self.right.type
                self.left = self.right.left
                self.right = self.right.right

            #zero on right
            elif self.right.type == NodeType.number and self.right.val == '0':
                #return self.left
                self.val = self.left.val
                self.type = self.left.type
                self.right = self.left.right
                self.left = self.left.left
        return self

    def multiplicative_identity(self):
        """
        Reduce multiplicative identities
        x * 1 = x
        """
        if self.type == NodeType.operator:

            # Recursively simplify left and right subtrees, if they exist
            # ;;> This is the right way!
            if self.left:
                    self.left.multiplicative_identity()
            if self.right:
                    self.right.multiplicative_identity()
        
            if self.val == '*':
        
                # one on left
                if self.left and self.left.type == NodeType.number and self.left.val == '1':
                    self.val = self.right.val
                    self.type = self.right.type
                    #checks existence
                    if self.right:
                        self.left = self.right.left
                    else:
                        False
                    if self.right:
                        self.right = self.right.right
                    else:
                        False

                # one on right
                elif self.right and self.right.type == NodeType.number and self.right.val == '1':
                    self.val = self.left.val
                    self.type = self.left.type
                    #checks existence
                    if self.left:
                        self.left = self.left.left    
                    else:
                        False
                    if self.left:
                             self.right = self.left.right
                    else:
                        False

        #return after modification
        return self

     #OPTIONAL IMPLEMENTS
    def mult_by_zero(self):
        """
        Reduce multiplication by zero
        x * 0 = 0
        """
        # Optionally, IMPLEMENT ME! (I'm pretty easy)
        pass
    
    def constant_fold(self):
        """
        Fold constants,
        e.g. 1 + 2 = 3
        e.g. x + 2 = x + 2
        """
        # Optionally, IMPLEMENT ME! This is a bit more challenging. 
        # You also likely want to add an additional node type to your AST
        # to represent identifiers.
        pass            

    def simplify_binops(self):
        """
        Simplify binary trees with the following:
        1) Additive identity, e.g. x + 0 = x
        2) Multiplicative identity, e.g. x * 1 = x
        3) Extra #1: Multiplication by 0, e.g. x * 0 = 0
        4) Extra #2: Constant folding, e.g. statically we can reduce 1 + 1 to 2, but not x + 1 to anything
        """
        prev = None
        curr = self.prefix_str

        # loops until can't be simplified further
        while prev != curr:
            # storing how tree was
            prev = curr

            # simplifying, order matters for some expressions
            # not with in scope of class
            self.additive_identity()
            self.multiplicative_identity()
            #self.mult_by_zero()
            #self.constant_fold()

            # getting tree rep.
            curr = self.prefix_str

        return self

#unit test class to run the tests
class testRunner(unittest.TestCase):
    #test for additive identity
    #print statements added for tracking which tests on what files pass/fail
    def test_add_ident(self):
        print('\nTesting additive identity function: ')
        indir = osjoin('testbench','arith_id','inputs') 
        outdir = osjoin('testbench','arith_id','outputs')

        for file in os.listdir(indir):

            inpath = osjoin(indir, file)
            outpath = osjoin(outdir, file)

            with open(inpath, 'r') as accessed_file:
                print(f'Opening filepath {indir}/{file}')
                indata = list(accessed_file.read().strip().split())

            with open(outpath, 'r') as accessed_file:
                print(f'Opening filepath {outdir}/{file}')
                expected = accessed_file.read().strip()

            testExp = BinOpAst(indata).additive_identity()

            actual = testExp.prefix_str()
            
            self.assertEqual(actual, expected, f'Failed on file {file}')
            print(f"Success on test {file}!\n")

    #test for additive identity
    def test_mult_id(self):
        print('\n\nTesting multiplicative identity function: ')
        indir = osjoin('testbench','mult_id','inputs') 
        outdir = osjoin('testbench','mult_id','outputs')

        for file in os.listdir(indir):

            inpath = osjoin(indir, file)
            outpath = osjoin(outdir, file)

            with open(inpath, 'r') as accessed_file:
                print(f'Opening filepath {indir}/{file}')
                indata = list(accessed_file.read().strip().split())

            with open(outpath, 'r') as accessed_file:
                print(f'Opening filepath {outdir}/{file}')
                expected = accessed_file.read().strip()

            testExp = BinOpAst(indata).multiplicative_identity()

            actual = testExp.prefix_str()
            
            self.assertEqual(actual, expected, f'Failed on file {file}')
            print(f"Success on test {file}!\n")


    def test_simplify(self):
        print('\n\nTesting simplify_binops function: ')
        indir = osjoin('testbench','combined','inputs') 
        outdir = osjoin('testbench','combined','outputs')

        for file in os.listdir(indir):

            inpath = osjoin(indir, file)
            outpath = osjoin(outdir, file)

            with open(inpath, 'r') as accessed_file:
                print(f'Opening filepath {indir}/{file}')
                indata = list(accessed_file.read().strip().split())

            with open(outpath, 'r') as accessed_file:
                print(f'Opening filepath {outdir}/{file}')
                expected = accessed_file.read().strip()

            testExp = BinOpAst(indata).simplify_binops()

            actual = testExp.prefix_str()
            
            self.assertEqual(actual, expected, f'Failed on file {file}')
            print(f"Success on all test cases!")




if __name__ == "__main__":
    #runs implemented testRunner
    unittest.main()
