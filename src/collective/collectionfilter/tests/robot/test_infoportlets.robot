
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Default Setup
Test Teardown  Default Teardown


*** Test Cases ***************************************************************

Scenario: Info on single choice filter
    Given I've got a site with a collection
      and my collection has a collection filter  Subject
      and my collection has a collection info  Current Filters  value_quoted_filter
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then Should be Info with text: "Süper" Subject

Scenario: Info on multiple choice filter
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  filter_colon_value
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
     then Should be Info with text: Subject: Süper/Evänt

Scenario: Info on result count
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  result_count  
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then Should be Info with text: 2

Scenario: Info on keyword search
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  search_quoted  
      and my collection has a collection search
     When I'm viewing the collection
      and I search for "Document"
     then Should be Info with text: "Document"

Scenario: Combine info templates
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  search_for  search_quoted  filter_colon_value  comma  with  result_count  results
      and my collection has a collection search
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
      and I search for "Event"
     Then Should be Info with text: Search for "Event" Subject: Süper/Evänt, with 1 result

Scenario: Hide on any filter
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  result_count   hide_when=any_filter
      and my collection has a collection filter  Subject
     When I'm viewing the collection
      and Should be Info with text: 3
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then should be no Info
      and Click Input "All (3)"
     then Should be Info with text: 3
      and Click Input "Süper (2)"
     then should be no Info

Scenario: Display as title
    Given I've got a site with a collection
      and my collection has a collection info  Current Filters  search_for  search_quoted  filter_colon_value  comma  with  result_count  results  as_title=${True}
      and my collection has a collection filter  Subject
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
     then Should be Info with text: Subject: Süper, with 2 results
      and run keyword if  ${USE_TILES}  Page Should Contain Element   css=h1  limit=2