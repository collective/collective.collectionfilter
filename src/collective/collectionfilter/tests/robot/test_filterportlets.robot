
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Default Setup
Test Teardown  Default Teardown




*** Test Cases ***************************************************************

Scenario: Add filter to collection
    Given I've got a site with a collection
      and my collection has a collection search
      and my collection has a collection filter  Subject  or  checkboxes_dropdowns
      and my collection has a collection sorting  sortable_title
     When I'm viewing the collection
     then Should be 3 collection results
     When Click Input "Dokumänt (2)"
     then Should be 2 collection results
     When Click Input "All (3)"
     then Should be 3 collection results

Scenario: Test Batching

    Given I've got a site with a collection  batch=1
      and my collection has a collection filter  Subject  or  checkboxes_dropdowns
      and I'm viewing the collection
     then Should be 1 collection results
     when Click Input "Süper (2)"
     then Should be 1 collection results
      and Should be 1 pages
     when Click Page "1"
     then Should be 1 collection results
     then Should be 1 pages

    ${loc}=  get location
    should contain  ${loc}  collectionfilter=1

Scenario: Hide when no options

    Given I've got a site with a collection
      and my collection has a collection filter  author_name  or  checkboxes_dropdowns  Hide if empty
     When I'm viewing the collection
     then Should be 3 collection results
     then Should be 0 filter options


Scenario: show hidden filter if just narrowed down

    Given I've got a site with a collection
      and my collection has a collection filter  Type  single  checkboxes_dropdowns  Narrow down filter options
     When I'm viewing the collection
      and Should be 3 filter options

      and Select Filter Option "Event (1)"
      and Should be 2 filter options

Scenario: hide hidden filter if just narrowed down
    Given I've got a site with a collection
      and my collection has a collection filter  Type  single  checkboxes_dropdowns  Narrow down filter options  Hide if empty
     When I'm viewing the collection
      and Should be 3 filter options

    # But if we filter it down it shouldn't disappear as then we have no way to click "All" to get back
      and Select Filter Option "Event (1)"
     Then Should be 2 filter options


Scenario: Displaying multiple collection filters on a single page
    Given I've got a site with a collection
      and my collection has a collection filter
      and my collection has a collection filter  group_by=Type
    When I'm viewing the collection
    Then I should have a filter with 4 options
      and I should have a filter with 3 options
      and I should see 7 filter options on the page

Scenario: Combine search and OR filter
    Given I've got a site with a collection
      and my collection has a collection search
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Click Input "Süper (2)"
      and Should be 2 collection results
      and Click Input "Evänt (1)"
      and Should be 1 collection results
      and I search for "Event"
      and Should be 1 collection results
