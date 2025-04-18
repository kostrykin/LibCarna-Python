import gc
import unittest

import faulthandler
faulthandler.enable()

import carna

extra_checks = hasattr(carna.base, 'debug_events')


class CarnaTestCase(unittest.TestCase):

    def setUp(self):
        if extra_checks:
            carna.base.debug_events()  # Clear events before the test starts

    def tearDown(self):
        if extra_checks:
            gc.collect()
            debug_events = carna.base.debug_events()
            memory_leaks, double_frees = analyze_debug_events(debug_events)
            self.assertEqual(memory_leaks, 0, f"Memory leaks detected: {memory_leaks}")
            self.assertEqual(double_frees, 0, f"Double frees detected: {double_frees}")


def analyze_debug_events(debug_events):
    allocations = set()
    double_frees = 0
    for event_str in debug_events:
        event = event_str.split(': ')
        match event[1]:
            case 'created':
                allocations.add(event[0])
            case 'deleted':
                if event[0] in allocations:
                    allocations.remove(event[0])
                else:
                    double_frees += 1
    memory_leaks = len(allocations)
    return memory_leaks, double_frees