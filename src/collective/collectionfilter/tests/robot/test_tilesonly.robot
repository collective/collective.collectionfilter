
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Default Setup
Test Teardown  Default Teardown




*** Test Cases ***************************************************************

Scenario: Add filter before content listing
    Given I've got a site without a listing
      and my collection has a collection filter  Subject  or  checkboxes_dropdowns
     then Page should contain  need to add a Content Listing