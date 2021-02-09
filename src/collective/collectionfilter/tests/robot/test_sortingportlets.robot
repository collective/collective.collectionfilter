
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
