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
# WSGI_SERVER_HOST=localhost WSGI_SERVER_PORT=50003 robot src/collective/collectionfilter/tests/robot/test_sortingportlets.robot
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

Scenario: Sorting with result sorting portlet
    Given I've got a site with a collection
      and my collection has a collection sorting
      and I'm viewing the collection
     When I sort by "Sortable Title"
     Then Page should not contain   Error
      and Results are Sorted

# Scenario: Combine sort and OR filter
#     Given I've got a site with a collection
#       and my collection has a collection sorting
#       and my collection has a collection filter  Subject  and  checkboxes_dropdowns
#      When I'm viewing the collection
#       and Click Input "Süper (2)"
#       and Should be 2 collection results
#       and Click Input "Evänt (1)"
#       and Should be 1 collection results
#      Then I sort by "Sortable Title"
#       and Page should not contain  Error
#       and Should be 1 collection results
#       and Results are Sorted
