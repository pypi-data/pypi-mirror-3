from unittest import TestCase

#
# Define some utility functions first, which will be 
# useful for testing.  
# 

from operator import add
p_even = lambda x: (x % 2 == 0)
p_odd = lambda x: not(p_even(x))
p_medium = lambda seq: len(seq) > 3
p_long = lambda seq: len(seq) > 12
f_inc = lambda x: x+1
f_dbl = lambda x: x*2

#
# Now on to the actual tests...
#

class TestListUtils(TestCase):
    def setUp(self):
        self.simple_list = [1,2,3,4,5,6]

from list115utils import ego
class TestEgo(TestListUtils):
    def test_ego_returns_same_integer(self):
        self.assertEqual(ego(5), 5)

    def test_ego_returns_same_list(self):
        self.assertEqual(ego(self.simple_list), self.simple_list)

    def test_ego_on_empty_list_returns_empty_list(self):
        self.assertEqual(ego([]), [])

    def test_ego_on_empty_list_is_not_none(self):
        self.assertNotEqual(ego([]), None)

    def test_ego_on_none_is_none(self):
        self.assertEqual(ego(None), None)

from list115utils import p_true
class TestPTrue(TestListUtils):
    def test_p_true_is_true_on_true_input(self):
        self.assertTrue(p_true(True))

    def test_p_true_is_true_on_false_input(self):
        self.assertTrue(p_true(False))

    def test_p_true_is_true_on_null_input(self):
        self.assertTrue(p_true(None))

from list115utils import p_false
class TestPFalse(TestListUtils):
    def test_p_false_is_false_on_true_input(self):
        self.assertFalse(p_false(True))

    def test_p_false_is_false_on_false_input(self):
        self.assertFalse(p_false(False))

    def test_p_false_is_false_on_null_input(self):
        self.assertFalse(p_false(None))

from list115utils import compose
class TestCompose(TestListUtils):
    def test_compose_returns_result_of_composition(self):
        self.assertEqual(compose(f_dbl, f_inc)(5), (5+1)*2)

from list115utils import remove_if
class TestRemoveIf(TestListUtils):
    def test_remove_if_removes_even_elements(self):
        self.assertEqual(remove_if(p_even, self.simple_list), [1,3,5])

    def test_remove_if_removes_odd_elements(self):
        self.assertEqual(remove_if(p_odd, self.simple_list), [2,4,6])

    def test_remove_if_doesnt_remove_unmatching_elements(self):
        self.assertEqual(remove_if(p_even, [1,3]), [1,3])

    def test_remove_if_works_on_empty_lists(self):
        self.assertEqual(remove_if(p_odd, []), [])

from list115utils import foldr
class TestFoldr(TestListUtils):
    def test_foldr_can_do_addition(self):
        self.assertEqual(foldr(add, 1, self.simple_list), 22)

    def test_fold_works_on_empty_list(self):
        self.assertEqual(foldr(add, 2, []), 2)

from list115utils import xfoldr
class TestXFoldr(TestListUtils):
    def test_xfoldr_can_produce_sum(self):
        xsum = xfoldr(add, 0)
        self.assertEqual(xsum(self.simple_list), sum(self.simple_list))

from list115utils import map0_n
class TestMap0n(TestListUtils):
    def test_map0_n_can_shift_up(self):
        self.assertEqual(map0_n(f_inc, 6), self.simple_list)

    def test_map0_n_can_double(self):
        self.assertEqual(map0_n(f_dbl, 5), [0,2,4,6,8])

    def test_map0_works_for_zero(self):
        self.assertEqual(map0_n(f_dbl, 0), [])

from list115utils import map1_n
class TestMap1n(TestListUtils):
    def test_map1_n_can_shift(self):
        self.assertEqual(map1_n(f_inc, 5), [2,3,4,5,6])

    def test_map1_n_can_double(self):
        self.assertEqual(map1_n(f_dbl, 5), [2,4,6,8,10])

    def test_map1_n_works_with_zero(self):
        self.assertEqual(map1_n(f_dbl, 0), [])

from list115utils import empty_lists
class TestEmptyLists(TestListUtils):
    def test_empty_lists_returns_correct_number_of_lists(self):
        self.assertSequenceEqual(list(empty_lists(5)), [[],[],[],[],[]])

    def test_empty_lists_works_with_1(self):
        self.assertSequenceEqual(list(empty_lists(1)), [[]])

    def test_empty_lists_works_with_0(self):
        self.assertSequenceEqual(list(empty_lists(0)), [])

from list115utils import listor_
class TestListOr_(TestListUtils):
    def test_listor__with_zeros_and_mixed_integers(self):
        self.assertEqual(listor_([0,0,3,0]), 3)

    def test_listor__with_false_items_only(self):
        self.assertFalse(listor_([False, False, False]))

    def test_listor__with_mixed_booleans(self):
        self.assertTrue(listor_([True, False]))

    def test_listor__with_non_zero_integers(self):
        self.assertEqual(listor_([-1,3,4]), -1)

from list115utils import flatten
class TestFlatten(TestListUtils):
    def test_flatten_works_on_shallow_list(self):
        l = [[1], [2, 3], [], [4, 5], [6,]]
        self.assertListEqual(flatten(l), self.simple_list)

    def test_flatten_does_shallow_flatten_on_deeply_nested_list(self):
        l = [['1', ['apple', 'orange'], [], '3'], [4,5,6], [], ['b']]
        self.assertListEqual(flatten(l), ['1', ['apple', 'orange'], [], '3', 4, 5, 6, 'b'])

    def test_flatten_works_on_empty_list(self):
        self.assertListEqual(flatten([]), [])

from list115utils import flatten_deep
class TestFlattenDeep(TestListUtils):
    def test_flatten_deep_works_on_mixed_deep_lists(self):
        l = ['a', ['1', ['apple', 'orange'], [], '3'], [4,5,6], [], 'b']
        self.assertListEqual(flatten_deep(l), ['a', '1', 'apple', 'orange', '3', 4, 5, 6, 'b'])

    def test_flatten_deep_works_on_empty_list(self):
        self.assertListEqual(flatten_deep([]), [])

from list115utils import which, p_true
class TestWhich(TestListUtils):
    def setUp(self):
        self.items = ['a', 'abc', 'abcd', 'abcde', 'ad', 'def', 'defg', '', 'hijklmn']
    def test_which_selects_the_right_positions(self):
        self.assertEqual(which(p_medium, self.items), 2)

    def test_which_returns_negative_one_if_not_found(self):
        self.assertEqual(which(p_long, self.items), -1)

    def test_which_returns_0_for_tautology(self):
        self.assertEqual(which(p_true, self.items), 0)

from list115utils import subdict
class TestSubdict(TestListUtils):
    def setUp(self):
        self.test_dict = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6}

    def test_subdict_returns_the_right_dictionary(self):
        self.assertDictEqual(
                subdict(self.test_dict, 'ace'), 
                {'a':1, 'c':3, 'e':5})

    def test_subdict_returns_only_present_items(self):
        self.assertDictEqual(subdict(self.test_dict, 'dof'), {'d':4, 'f':6})

    def test_subdict_returns_empty_dict_if_no_match(self):
        self.assertDictEqual(subdict(self.test_dict, 'gut'), {})

from list115utils import tuplify
class TestTuplify(TestListUtils):
    def setUp(self):
        self.test_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

    def test_tuplify_returns_proper_2_tuples(self):
        self.assertSequenceEqual(tuplify(self.test_list), [('a', 'b'), ('c', 'd'), ('e', 'f'), ('g', 'h'), ('i', 'j')])
    
    def test_tuplify_returns_proper_3_tuples(self):
        self.assertSequenceEqual(tuplify(self.test_list, n=3), [('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'h', 'i'), ('j', ), ])
    
    def test_tuplify_work_with_short_lists(self):
        self.assertSequenceEqual(tuplify([1,2,3], n=4), [(1,2,3), ])

from list115utils import set_attrs_from_dict
class TestSetAttrsFromDict(TestListUtils):
    def setUp(self):
        self.test_dict = {'a':1, 'b':2, 'c':3, 'd':4, }
        class C(object):
            def __init__(self):
                self.a = ''
                self.b = ''
        self.obj = C()

    def test_set_attrs_from_dict_returns_correct_set(self):
        set_attrs_from_dict(self.obj, self.test_dict, ['a', 'c'])
        self.assertEqual(self.obj.a, 1)
        self.assertEqual(self.obj.c, 3)
