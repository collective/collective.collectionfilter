# -*- coding: utf-8 -*-
from collective.collectionfilter.testing import (
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING,
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED,
    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED,
)  # noqa
from plone.app.testing import ROBOT_TEST_LEVEL
from plone.testing import layered
from plone import api

import os
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in os.listdir(robot_dir)
        if doc.endswith('.robot') and doc.startswith('test_')
    ]
    for robot_test in robot_tests:
        if "ajaxenabled" in robot_test:
            if api.env.plone_version() < '5.1':
                break
            else:
                test_layer = (
                    COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_ENABLED
                )
        elif "ajaxdisabled" in robot_test:
            test_layer = (
                COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING_AJAX_DISABLED
            )

        else:
            test_layer = COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING

        robottestsuite = robotsuite.RobotTestSuite(robot_test)
        robottestsuite.level = ROBOT_TEST_LEVEL
        suite.addTests([layered(robottestsuite, layer=test_layer)])

    return suite
