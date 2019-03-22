# ============================================================================
# EXAMPLE ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s collective.collectionfilter -t test_example.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src collective.collectionfilter.testing.COLLECTIVE_COLLECTIONFILTER_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/collective/collectionfilter/tests/robot/test_example.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a member I want to be able to log into the website
  [Documentation]  Example of a BDD-style (Behavior-driven development) test.
  Given a login form
   When I enter valid credentials
   Then I am logged in

