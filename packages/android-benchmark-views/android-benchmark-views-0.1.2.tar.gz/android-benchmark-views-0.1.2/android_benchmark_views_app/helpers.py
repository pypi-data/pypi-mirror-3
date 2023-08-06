'''
Module for non-database helper functions
'''

from decimal import Decimal
from dashboard_app import models as lava_models
from django.db.models import StdDev, Avg

import sys

def _get_tests(bundle):
    '''
    returns a unique list of tests that were a part of this bundle
    '''
    tests = []
    seen = {}

    for test_run in lava_models.TestRun.objects.filter(bundle=bundle):
        name = test_run.test.test_id
        if name in seen or name == 'lava': continue
        seen[name] = 1
        tests.append(test_run.test)

    return tests

def _b_is_b_str(test):
    if test.test_id == 'Totals':
        return ''

    if test.test_id == 'skia':
        return "Smaller is better"
    return "Bigger is better"

def _get_test_result_averages(bundle, test):
    avgs = lava_models.TestResult.objects.filter(
                test_run__bundle=bundle, test_case__test=test). \
                values('test_case__test_case_id'). \
                annotate(std_dev=StdDev('measurement'), average=Avg('measurement')). \
                order_by('relative_index')

    return avgs

def _get_totals_default(test_result_averages):
    total = 0.0
    for tra in test_result_averages:
        total += tra['average']
    return total

def _get_v8_totals(test_result_averages):
    lastidx = test_result_averages.count()
    return test_result_averages[lastidx-1]['average']

def _add_totals(test_averages):
    ''' prepends a summary of totals to the list '''
    thismodule = sys.modules[__name__]

    tra = []

    for ta in test_averages:
        fname = "__get_%s_totals" % ta['test']
        func = getattr(thismodule, fname, _get_totals_default)
        total = func(ta['test_result_averages'])
        tra.append({'test_case__test_case_id':ta['test'], 'average': total, 'std_dev': 0})

    test_averages.insert(0, {
            'test': 'Totals',
            'b_is_b_str': '',
            'test_result_averages': tra,
        })

def benchmark_run_test_averages(benchmarkrun):
    '''
    Benchmark runs will consist of multiple runs of a test like "v8".
    This function performs queries on the test results in the benchmark
    run to build up average/deviation metrics for each test result.

    Returns a data structure suitable for the run.html template in the
    format like:
       [
        {'test': 'v8',
         'b_is_b_str': 'Bigger is better',
         'test_result_averages': [
            {
                'test_case__test_case_id': 'Richards',
                'average': 10.2,
                'std_dev': .122
            },
         ]
        },
       ]
    '''
    bundle = benchmarkrun.bundle
    test_averages = []
    for test in _get_tests(bundle):
        test_averages.append({
            'test': test.test_id,
            'test_result_averages':_get_test_result_averages(bundle, test),
            'b_is_b_str': _b_is_b_str(test)
        })
    _add_totals(test_averages)
    return test_averages


