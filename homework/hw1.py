# .. -*- coding: utf-8 -*-
#
# ********************************
# hw1.py -- Homework 1 assignment.
# ********************************
# This file must be named ``hw1.py``; none of the function names below are allowed
# to change.
#
# Code skeleton
# =============
# Pick a value from a sequence of items.
def pick_val(
  # The sequence to pick from.
  seq,
  #
  # The index of the element to select, measured from the end of the list. That is,
  # 1 refers to the last item in seq, 2 to the second item from the end, etc.
  # This parameter defaults to the 4th from the end.
  #
  # * If the sequence is shorter than 4 elements, select the third, second,
  #   first, or raise an IndexError exception if the sequence is empty.
  # * If the index is negative, select from the beginning of the list:
  #   index == -2 returns seq[2]. Again, if the list is less than index in
  #   length, return an earlier value.
  index=4):

# Joey's Code
# ===========
# This is used to make the code read from right to left, and if
# the sequence is shorter than the index it returns the value at the zero
# location:
    if(len(seq) > index):
        return (seq[len(seq) - index])
    else:
        return seq[0]
# This is used to handle the case when given a negative index:
    if (index < 0):
        return (seq[index * (-1)])
# This is used to handle the case where the sequence is empty:
    if (len(seq) ==0):
        raise IndexError
# At this point all integers have been accounted for.  Then if the index
# is not a string raise a type error.
    if (index != type(str)):
        raise TypeError

    pass

# Tests
# =====
class TestPickVal(object):
    # Test picking from a list with > 4 elements.
    def test_1(self):
        assert pick_val(range(10)) == 6

    # Test picking from a list with exactly 4 elements.
    def test_2(self):
        assert pick_val(range(4)) == 0

    # Test picking from a list with < 4 elements.
    def test_3(self):
        assert pick_val(range(3)) == 0
        assert pick_val(range(2)) == 0
        assert pick_val(range(1)) == 0

    # Test picking from an empty list.
    def test_4(self):
        try:
            pick_val([])
            assert False
        except IndexError:
            pass

    # Test passing a non-integral type for the index.
    def test_5(self):
        try:
            pick_val(range(10), 1.5)
            assert False
        except TypeError:
            pass

    # Test picking values outside the range.
    def test_6(self):
        assert pick_val(range(10), 11) == 0

    # Test picking values from other types (string, tuple).
    def test_7(self):
        assert pick_val('hello') == 'e'
        assert pick_val('hello', 10) == 'h'
        assert pick_val('hello', 1) == 'o'

        assert pick_val(tuple(range(10))) == 6
        assert pick_val(tuple(range(10)), 3) == 7
        assert pick_val(tuple(range(10)), 11) == 0

# Test driver code
# ================
def run_tests():
    tpv = TestPickVal()
    tpv.test_1()
    tpv.test_2()
    tpv.test_3()
    tpv.test_4()
    tpv.test_5()
    tpv.test_6()
    tpv.test_7()
    print('All tests passed.')

if __name__ == '__main__':
    run_tests()
