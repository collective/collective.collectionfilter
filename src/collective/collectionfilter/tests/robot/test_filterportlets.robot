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

Scenario: Add filter portlets to collection

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Click link  link:Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click link  link:Right column

    Add search portlet
    Add filter portlet  Subject  or  checkboxes_dropdowns

    Click link  css=a.link-parent
    Xpath should match X times  //article[@class='entry']  2

    Click element  css=li.filter-dokumant.checkbox input
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  1

    Click element  css=li.filter-all.checkbox input
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  2

    Input text  css=.collectionSearch input[name='SearchableText']  Docu
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  1

    # XXX fails right now ... needs to be fixed in JS
    #Clear element text  css=.collectionSearch input[name='SearchableText']
    #Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  2

