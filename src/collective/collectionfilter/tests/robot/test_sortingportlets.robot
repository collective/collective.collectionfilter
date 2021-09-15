
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Default Setup
Test Teardown  Default Teardown


*** Test Cases ***************************************************************

Scenario: Sorting with result sorting portlet
    Given I've got a site with a collection
      and my collection has a collection sorting
      and I'm viewing the collection
      and I sort by "Sortable Title"
      and Page should not contain   Error
      and Results are Sorted

Scenario: Combine sort and OR filter
    Given I've got a site with a collection
      and my collection has a collection sorting
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
     Then I sort by "Sortable Title"
      and Page should not contain  Error
      and Should be 1 collection results
      and Results are Sorted
