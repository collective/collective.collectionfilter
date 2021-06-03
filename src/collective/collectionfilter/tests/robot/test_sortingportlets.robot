
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Default Teardown


*** Test Cases ***************************************************************

Scenario: Sorting with result sorting portlet
    Given I've got a site with a collection
      and my collection has a collection sorting portlet
      and I'm viewing the collection

    I sort by "sortable_title"
      and I should not have a portlet titled "Error"

Scenario: Combine sort and OR filter
    Given I've got a site with a collection
      and my collection has a collection sorting portlet
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
     Then I sort by "sortable_title"
      and Should be 1 collection results
      and I should not have a portlet titled "Error"
