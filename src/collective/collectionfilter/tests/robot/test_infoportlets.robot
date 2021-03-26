
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

Scenario: Info on multiple choice filter
    Given I've got a site with a collection
      and my collection has a collection info portlet  filter_colon_value  Current Filters
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
     then I should have a portlet titled "Current Filters" with text Subject: Süper/Evänt

Scenario: Info on result count
    Given I've got a site with a collection
      and my collection has a collection info portlet  result_count  Current Filters
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then I should have a portlet titled "Current Filters" with text 2

Scenario: Info on keyword search
    Given I've got a site with a collection
      and my collection has a collection info portlet  search_quoted  Current Filters
      and my collection has a collection search portlet
     When I'm viewing the collection
      and I search for "Document" with ajax
     then I should have a portlet titled "Current Filters" with text "Document"
