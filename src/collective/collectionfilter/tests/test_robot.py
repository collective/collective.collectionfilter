# -*- coding: utf-8 -*-
from collective.collectionfilter.testing import (  # noqa
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
)
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
)
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
)
from plone import api
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered

import os
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, "robot")
    robot_tests = [
        os.path.join("robot", doc)
        for doc in os.listdir(robot_dir)
        if doc.endswith(".robot") and doc.startswith("test_")
    ]
    for robot_test in robot_tests:
        if api.env.plone_version() < "5.1" and "ajaxenabled" in robot_test:
            continue
        elif "ajaxenabled" in robot_test:
            test_layer = (
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
                ),
            )
        elif "ajaxdisabled" in robot_test:
            test_layer = (
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
                ),
            )
        elif "_tiles" in robot_test:
            test_layer = (
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
                ),
            )
        elif api.env.plone_version() < "5.1":
            test_layer = (
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
                ),
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
                ),
            )
        else:
            # We will run generic tests with and without ajax to test everything
            test_layer = (
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_TILES,
                ),
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
                ),
                (
                    ROBOT_TEST_LEVEL,
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
                ),
            )
        for level, layer in test_layer:
            robottestsuite = robotsuite.RobotTestSuite(robot_test)
            robottestsuite.level = level
            suite.addTests([layered(robottestsuite, layer=layer)])

    return suite
