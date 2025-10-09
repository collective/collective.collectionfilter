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
# WSGI_SERVER_HOST=localhost WSGI_SERVER_PORT=50003 robot src/collective/collectionfilter/tests/robot/test_tilesonly.robot
#

*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

# disable headless mode for browser
# set the variable BROWSER to chrome or firefox
*** Variables ***
${BROWSER}    chrome

*** Test Cases ***

Scenario: Add filter before content listing
    Go to  ${PLONE_URL}/mycollection
#     Given I've got a site without a listing
#      When Open advanced mosaic editor
#       and Add filter tile  Subject  or  checkboxes_dropdowns
#       and Add search tile
#       and Save mosaic page
#      When My collection has a collection sorting tile
#       and Save mosaic page
#      then Page should contain  need to add a Content Listing
#      When edit mosaic page
#       and Add contentlisting tile
#       and save mosaic page
#      then Page should not contain  need to add a Content Listing
