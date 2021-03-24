
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Default Teardown


*** Test Cases ***************************************************************

Scenario: Info on single choice filter
    Given I've got a site with a collection
      and my collection has a collection info portlet  value_quoted_filter  Current Filters
      and my collection has a collection filter portlet  Subject
    When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then I should have a portlet titled "Current Filters" with text "Süper" Subject
