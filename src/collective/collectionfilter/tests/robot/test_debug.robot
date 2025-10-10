# Start a single robot test
#
# Install rfbrowser
#
# rfbrowser init
#
# Start the server
#
# WSGI_SERVER_HOST=localhost WSGI_SERVER_PORT=50003 robot-server collective.collectionfilter.testing.ACCEPTANCE_TESTING
#
# Start the test
#
# WSGI_SERVER_HOST=localhost WSGI_SERVER_PORT=50003 robot src/collective/collectionfilter/tests/robot/test_debug.robot
#

*** Settings ***

Resource    keywords.robot

Test Setup    Run Keywords    Default Setup
Test Teardown    Run keywords     Default Teardown

# disable headless mode for browser
# set the variable BROWSER to chrome or firefox
#*** Variables ***
#${BROWSER}    chrome


*** Test Cases ***

Scenario: Add filter to collection
    Given a logged in test-user
      and a test collection view
      and a manage portlets view
     When I add filter portlet    exclude_from_nav    single    checkboxes_radiobuttons
      and I add filter portlet    Subject    or    checkboxes_radiobuttons
      and I add filter portlet    portal_type    or    checkboxes_radiobuttons
     Then Go to  ${PLONE_URL}/mycollection

*** Keywords ***

a test collection view
    Go to  ${PLONE_URL}/mycollection
