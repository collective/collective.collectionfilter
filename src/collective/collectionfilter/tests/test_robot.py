# -*- coding: utf-8 -*-
from collective.collectionfilter.testing import (  # noqa
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
)
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
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
    l1 = ROBOT_TEST_LEVEL
    l2 = ROBOT_TEST_LEVEL + 1
    for robot_test in robot_tests:
        if api.env.plone_version() < "5.1" and "ajaxenabled" in robot_test:
            continue
        elif api.env.plone_version() < "5.1":
            test_layer = (
                (l1, COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED),
            )
        elif "ajaxenabled" in robot_test:
            test_layer = (
                (l1, COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED),
            )
        elif "ajaxdisabled" in robot_test:
            test_layer = (
                (l1, COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED),
            )
        else:
            # We will run generic tests with and without ajax to test everything
            test_layer = (
                (l2, COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED),
                (l1, COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED),
            )
        for level, layer in test_layer:
            robottestsuite = robotsuite.RobotTestSuite(robot_test)
            robottestsuite.level = level
            suite.addTests([layered(robottestsuite, layer=layer)])

    return suite
