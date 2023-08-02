from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
)
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
)
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
)
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    test_layer_mapping = (
        (
            COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
            ("debug", "filterportlets", "sortingportlets"),
        ),
        (
            COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
            ("debug", "filterportlets", "sortingportlets"),
        ),
        (
            COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
            ("tilesonly",),
        ),
    )
    for layer, test_files in test_layer_mapping:
        for robot_test in test_files:
            robottestsuite = robotsuite.RobotTestSuite(f"robot/test_{robot_test}.robot")
            robottestsuite.level = ROBOT_TEST_LEVEL
            suite.addTests([layered(robottestsuite, layer=layer)])

    return suite
