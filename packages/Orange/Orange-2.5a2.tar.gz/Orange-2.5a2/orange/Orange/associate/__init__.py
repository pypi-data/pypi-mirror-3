"""
==============================
Induction of association rules
==============================

Orange provides two algorithms for induction of
`association rules <http://en.wikipedia.org/wiki/Association_rule_learning>`_.
One is the basic Agrawal's algorithm with dynamic induction of supported
itemsets and rules that is designed specifically for datasets with a
large number of different items. This is, however, not really suitable
for feature-based machine learning problems.
We have adapted the original algorithm for efficiency
with the latter type of data, and to induce the rules where, 
both sides don't only contain features
(like "bread, butter -> jam") but also their values
("bread = wheat, butter = yes -> jam = plum").

It is also possible to extract item sets instead of association rules. These
are often more interesting than the rules themselves.

Besides association rule inducer, Orange also provides a rather simplified
method for classification by association rules.

===================
Agrawal's algorithm
===================

The class that induces rules by Agrawal's algorithm, accepts the data examples
of two forms. The first is the standard form in which each example is
described by values of a fixed list of features (defined in domain).
The algorithm, however, disregards the feature values and only checks whether
the value is defined or not. The rule shown above ("bread, butter -> jam")
actually means that if "bread" and "butter" are defined, then "jam" is defined
as well. It is expected that most of values will be undefined - if this is not
so, use the :class:`~AssociationRulesInducer`.

:class:`AssociationRulesSparseInducer` can also use sparse data. 
Sparse examples have no fixed
features - the domain is empty. All values assigned to example are given as meta attributes.
All meta attributes need to be registered with the :obj:`~Orange.data.Domain`.
The most suitable format fot this kind of data it is the basket format.

The algorithm first dynamically builds all itemsets (sets of features) that have
at least the prescribed support. Each of these is then used to derive rules
with requested confidence.

If examples were given in the sparse form, so are the left and right side
of the induced rules. If examples were given in the standard form, so are
the examples in association rules.

.. class:: AssociationRulesSparseInducer

    .. attribute:: support
    
        Minimal support for the rule.
        
    .. attribute:: confidence
    
        Minimal confidence for the rule.
        
    .. attribute:: store_examples
    
        Store the examples covered by each rule and
        those confirming it.
        
    .. attribute:: max_item_sets
    
        The maximal number of itemsets. The algorithm's
        running time (and its memory consumption) depends on the minimal support;
        the lower the requested support, the more eligible itemsets will be found.
        There is no general rule for setting support - perhaps it 
        should be around 0.3, but this depends on the data set.
        If the supoort was set too low, the algorithm could run out of memory.
        Therefore, Orange limits the number of generated rules to
        :obj:`max_item_sets`. If Orange reports, that the prescribed
        :obj:`max_item_sets` was exceeded, increase the requered support
        or alternatively, increase :obj:`max_item_sets` to as high as you computer
        can handle.

    .. method:: __call__(data, weight_id)

        Induce rules from the data set.


    .. method:: get_itemsets(data)

        Returns a list of pairs. The first element of a pair is a tuple with 
        indices of features in the item set (negative for sparse data). 
        The second element is a list of indices supporting the item set, that is,
        all the items in the set. If :obj:`store_examples` is False, the second
        element is None.

We shall test the rule inducer on a dataset consisting of a brief description
of Spanish Inquisition, given by Palin et al:

    NOBODY expects the Spanish Inquisition! Our chief weapon is surprise...surprise and fear...fear and surprise.... Our two weapons are fear and surprise...and ruthless efficiency.... Our *three* weapons are fear, surprise, and ruthless efficiency...and an almost fanatical devotion to the Pope.... Our *four*...no... *Amongst* our weapons.... Amongst our weaponry...are such elements as fear, surprise.... I'll come in again.

    NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!
    
The text needs to be cleaned of punctuation marks and capital letters at beginnings of the sentences, each sentence needs to be put in a new line and commas need to be inserted between the words.

Data example (:download:`inquisition.basket <code/inquisition.basket>`):

.. literalinclude:: code/inquisition.basket
   
Inducing the rules is trivial (uses :download:`inquisition.basket <code/inquisition.basket>`)::

    import Orange
    data = Orange.data.Table("inquisition")

    rules = Orange.associate.AssociationRulesSparseInducer(data, support = 0.5)

    print "%5s   %5s" % ("supp", "conf")
    for r in rules:
        print "%5.3f   %5.3f   %s" % (r.support, r.confidence, r)

The induced rules are surprisingly fear-full: ::

    0.500   1.000   fear -> surprise
    0.500   1.000   surprise -> fear
    0.500   1.000   fear -> surprise our
    0.500   1.000   fear surprise -> our
    0.500   1.000   fear our -> surprise
    0.500   1.000   surprise -> fear our
    0.500   1.000   surprise our -> fear
    0.500   0.714   our -> fear surprise
    0.500   1.000   fear -> our
    0.500   0.714   our -> fear
    0.500   1.000   surprise -> our
    0.500   0.714   our -> surprise

To get only a list of supported item sets, one should call the method
get_itemsets::

    inducer = Orange.associate.AssociationRulesSparseInducer(support = 0.5, store_examples = True)
    itemsets = inducer.get_itemsets(data)
    
Now itemsets is a list of itemsets along with the examples supporting them
since we set store_examples to True. ::

    >>> itemsets[5]
    ((-11, -7), [1, 2, 3, 6, 9])
    >>> [data.domain[i].name for i in itemsets[5][0]]
    ['surprise', 'our']   
    
The sixth itemset contains features with indices -11 and -7, that is, the
words "surprise" and "our". The examples supporting it are those with
indices 1,2, 3, 6 and 9.

This way of representing the itemsets is memory efficient and faster than using
objects like :obj:`~Orange.data.variable.Variable` and :obj:`~Orange.data.Instance`.

.. _non-sparse-examples:

===================
Non-sparse data
===================

:class:`AssociationRulesInducer` works with non-sparse data.
Unknown values are ignored, while values of features are not (as opposite to
the algorithm for sparse rules). In addition, the algorithm
can be directed to search only for classification rules, in which the only
feature on the right-hand side is the class variable.

.. class:: AssociationRulesInducer

    All attributes can be set with the constructor. 

    .. attribute:: support
    
       Minimal support for the rule.
    
    .. attribute:: confidence
    
        Minimal confidence for the rule.
    
    .. attribute:: classification_rules
    
        If True (default is False), the classification rules are constructed instead
        of general association rules.

    .. attribute:: store_examples
    
        Store the examples covered by each rule and those
        confirming it
        
    .. attribute:: max_item_sets
    
        The maximal number of itemsets.

    .. method:: __call__(data, weight_id)

        Induce rules from the data set.

    .. method:: get_itemsets(data)

        Returns a list of pairs. The first element of a pair is a tuple with 
        indices of features in the item set (negative for sparse data). 
        The second element is a list of indices supporting the item set, that is,
        all the items in the set. If :obj:`store_examples` is False, the second
        element is None.

The example::

    import Orange

    data = Orange.data.Table("lenses")

    print "Association rules"
    rules = Orange.associate.AssociationRulesInducer(data, support = 0.5)
    for r in rules:
        print "%5.3f  %5.3f  %s" % (r.support, r.confidence, r)
        
The found rules are: ::

    0.333  0.533  lenses=none -> prescription=hypermetrope
    0.333  0.667  prescription=hypermetrope -> lenses=none
    0.333  0.533  lenses=none -> astigmatic=yes
    0.333  0.667  astigmatic=yes -> lenses=none
    0.500  0.800  lenses=none -> tear_rate=reduced
    0.500  1.000  tear_rate=reduced -> lenses=none
    
To limit the algorithm to classification rules, set classificationRules to 1: ::

    print "\\nClassification rules"
    rules = orange.AssociationRulesInducer(data, support = 0.3, classificationRules = 1)
    for r in rules:
        print "%5.3f  %5.3f  %s" % (r.support, r.confidence, r)

The found rules are, naturally, a subset of the above rules: ::

    0.333  0.667  prescription=hypermetrope -> lenses=none
    0.333  0.667  astigmatic=yes -> lenses=none
    0.500  1.000  tear_rate=reduced -> lenses=none
    
Itemsets are induced in a similar fashion as for sparse data, except that the
first element of the tuple, the item set, is represented not by indices of
features, as before, but with tuples (feature-index, value-index): ::

    inducer = Orange.associate.AssociationRulesInducer(support = 0.3, store_examples = True)
    itemsets = inducer.get_itemsets(data)
    print itemsets[8]
    
This prints out ::

    (((2, 1), (4, 0)), [2, 6, 10, 14, 15, 18, 22, 23])
    
meaning that the ninth itemset contains the second value of the third feature
(2, 1), and the first value of the fifth (4, 0).

=======================
Representation of rules
=======================

An :class:`AssociationRule` represents a rule. In Orange, methods for 
induction of association rules return the induced rules in
:class:`AssociationRules`, which is basically a list of :class:`AssociationRule` instances.

.. class:: AssociationRule

    .. method:: __init__(left, right, n_applies_left, n_applies_right, n_applies_both, n_examples)
    
        Constructs an association rule and computes all measures listed above.
    
    .. method:: __init__(left, right, support, confidence)
    
        Construct association rule and sets its support and confidence. If
        you intend to pass on such a rule you should set other attributes
        manually - AssociationRules's constructor cannot compute anything
        from arguments support and confidence.
    
    .. method:: __init__(rule)
    
        Given an association rule as the argument, constructor copies of the
        rule.
 
    .. attribute:: left, right
    
        The left and the right side of the rule. Both are given as :class:`Orange.data.Instance`.
        In rules created by :class:`AssociationRulesSparseInducer` from examples that
        contain all values as meta-values, left and right are examples in the
        same form. Otherwise, values in left that do not appear in the rule
        are "don't care", and value in right are "don't know". Both can,
        however, be tested by :meth:`~Orange.data.Value.is_special`.
    
    .. attribute:: n_left, n_right
    
        The number of features (i.e. defined values) on the left and on the
        right side of the rule.
    
    .. attribute:: n_applies_left, n_applies_right, n_applies_both
    
        The number of (learning) examples that conform to the left, the right
        and to both sides of the rule.
    
    .. attribute:: n_examples
    
        The total number of learning examples.
    
    .. attribute:: support
    
        nAppliesBoth/nExamples.

    .. attribute:: confidence
    
        n_applies_both/n_applies_left.
    
    .. attribute:: coverage
    
        n_applies_left/n_examples.

    .. attribute:: strength
    
        n_applies_right/n_applies_left.
    
    .. attribute:: lift
    
        n_examples * n_applies_both / (n_applies_left * n_applies_right).
    
    .. attribute:: leverage
    
        (n_Applies_both * n_examples - n_applies_left * n_applies_right).
    
    .. attribute:: examples, match_left, match_both
    
        If store_examples was True during induction, examples contains a copy
        of the example table used to induce the rules. Attributes match_left
        and match_both are lists of integers, representing the indices of
        examples which match the left-hand side of the rule and both sides,
        respectively.
   
    .. method:: applies_left(example)
    
    .. method:: applies_right(example)
    
    .. method:: applies_both(example)
    
        Tells whether the example fits into the left, right or both sides of
        the rule, respectively. If the rule is represented by sparse examples,
        the given example must be sparse as well.
    
Association rule inducers do not store evidence about which example supports
which rule. Let us write a function that finds the examples that
confirm the rule (fit both sides of it) and those that contradict it (fit the
left-hand side but not the right). The example::

    import Orange

    data = Orange.data.Table("lenses")

    rules = Orange.associate.AssociationRulesInducer(data, supp = 0.3)
    rule = rules[0]

    print
    print "Rule: ", rule
    print

    print "Supporting examples:"
    for example in data:
        if rule.appliesBoth(example):
            print example
    print

    print "Contradicting examples:"
    for example in data:
        if rule.applies_left(example) and not rule.applies_right(example):
            print example
    print

The latter printouts get simpler and faster if we instruct the inducer to
store the examples. We can then do, for instance, this: ::

    print "Match left: "
    print "\\n".join(str(rule.examples[i]) for i in rule.match_left)
    print "\\nMatch both: "
    print "\\n".join(str(rule.examples[i]) for i in rule.match_both)

The "contradicting" examples are then those whose indices are found in
match_left but not in match_both. The memory friendlier and the faster way
to compute this is as follows: ::

    >>> [x for x in rule.match_left if not x in rule.match_both]
    [0, 2, 8, 10, 16, 17, 18]
    >>> set(rule.match_left) - set(rule.match_both)
    set([0, 2, 8, 10, 16, 17, 18])

===============
Utilities
===============

.. autofunction:: print_rules

.. autofunction:: sort

"""

from orange import \
    AssociationRule, \
    AssociationRules, \
    AssociationRulesInducer, \
    AssociationRulesSparseInducer, \
    ItemsetNodeProxy, \
    ItemsetsSparseInducer

def print_rules(rules, ms = []):
    """
    Print the rules. If ms is left empty, only the rules are printed. If ms
    contains rules' attributes, e.g. ``["support", "confidence"]``, these are printed out as well.
    """
    if ms:
        print "\t".join([m[:4] for m in ms]) + "\trule"
        for rule in rules:
            print "\t".join(["%5.3f" % getattr(rule, m) for m in ms]) + "\t" + str(rule)
    else:
        for rule in rules:
            print rule

class __Cmp:
    def __init__(self, ms):
        self.ms = ms

    def __call__(self, r1, r2):        
        for m in self.ms:
            c = -cmp(getattr(r1, m), getattr(r2, m))
            if c:
                return c
        return 0

def sort(rules, ms = ["support"]):
    """
    Sort the rules according to the given criteria. The default key is "support"; list multiple keys in a list.
    """
    rules.sort(__Cmp(ms))
