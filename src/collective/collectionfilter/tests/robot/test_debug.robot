*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Test Setup  Run keyword  Default Setup
Test Teardown  Run keyword  Default Teardown


*** Test Cases ***************************************************************

Scenario: Add filter to collection
    Given a logged in manager
      and View a Test Collection
      and Manage portlets
      and Add filter portlet  exclude_from_nav  single  checkboxes_radiobuttons
      and Add filter portlet  Subject  or  checkboxes_radiobuttons
      and Add filter portlet  portal_type  or  checkboxes_radiobuttons
      Go to  ${PLONE_URL}/mycollection


*** Keywords *****************************************************************

View a Test Collection
    Go to  ${PLONE_URL}/mycollection
