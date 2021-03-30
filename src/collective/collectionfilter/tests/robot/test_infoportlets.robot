
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Default Teardown


*** Test Cases ***************************************************************

Scenario: Info on single choice filter
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  value_quoted_filter
      and my collection has a collection filter portlet  Subject
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then I should have a portlet titled "Current Filters" with text "Süper" Subject

Scenario: Info on multiple choice filter
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  filter_colon_value
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
     then I should have a portlet titled "Current Filters" with text Subject: Süper/Evänt

Scenario: Info on result count
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  result_count  
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then I should have a portlet titled "Current Filters" with text 2

Scenario: Info on keyword search
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  search_quoted  
      and my collection has a collection search portlet
     When I'm viewing the collection
      and I search for "Document"
     then I should have a portlet titled "Current Filters" with text "Document"

Scenario: Combine info templates
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  search_for  search_quoted  filter_colon_value  comma  with  result_count  results
      and my collection has a collection search portlet
      and my collection has a collection filter portlet  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
      and I search for "Event"
     Then I should have a portlet titled "Current Filters" with text Search for "Event" Subject: Süper/Evänt, with 1 result

Scenario: Hide on any filter
    Given I've got a site with a collection
      and my collection has a collection info portlet  Current Filters  value_quoted_filter   hide_when=any_filter
      and my collection has a collection filter portlet  Subject
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then I should not have a portlet titled "Current Filters"
