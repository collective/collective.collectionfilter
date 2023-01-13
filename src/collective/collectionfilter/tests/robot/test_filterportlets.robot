*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Test Setup  Run keyword  Default Setup
Test Teardown  Run keyword  Default Teardown


*** Test Cases ***************************************************************

Scenario: Add filter to collection
    Given I've got a site with a collection
      and my collection has a collection filter  Subject  or  checkboxes_dropdowns
     When I'm viewing the collection
     then Should be 6 collection results
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)
     When Click Input "Dokumänt (2)"
     then Should be 2 collection results
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)
     When Click Input "All (6)"
     then Should be 6 collection results
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)

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
      and my collection has a collection filter  Creator  or  checkboxes_dropdowns  Hide if empty
     When I'm viewing the collection
     then Should be 6 collection results
     then Should be 0 filter options


Scenario: show hidden filter if just narrowed down

    Given I've got a site with a collection
      and my collection has a collection filter  portal_type  single  checkboxes_dropdowns  Narrow down filter options
     When I'm viewing the collection
      and Should be filter options  All (6)  Event (1)  Page (5)
      and Select Filter Option "Event (1)"
     Then Should be filter options  All (6)  Event (1)

Scenario: don't hide hidden filter if just narrowed down
    Given I've got a site with a collection
      and my collection has a collection filter  portal_type  single  checkboxes_dropdowns  Narrow down filter options  Hide if empty
     When I'm viewing the collection
      and Should be filter options  All (6)  Event (1)  Page (5)
    # But if we filter it down it shouldn't disappear as then we have no way to click "All" to get back
      and Select Filter Option "Event (1)"
      Then Should be filter options  All (6)  Event (1)


Scenario: Displaying multiple collection filters on a single page
    Given I've got a site with a collection
      and my collection has a collection filter
      and my collection has a collection filter  group_by=portal_type
     When I'm viewing the collection
     Then I should have a filter with 7 options
      and I should have a filter with 3 options
      and I should see 10 filter options on the page
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)  All (6)  Event (1)  Page (5)

Scenario: Combine search and AND filter
    Given I've got a site with a collection
      and my collection has a collection search
      and my collection has a collection filter  Subject  and  checkboxes_dropdowns
     When I'm viewing the collection
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)
     Then Click Input "Süper (2)"
      and Should be 2 collection results
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)
     Then Click Input "Evänt (1)"
      and Should be 1 collection results
      and Should be filter checkboxes  All (6)  blue (1)  Dokumänt (2)  Evänt (1)  green (1)  red (1)  Süper (2)
     Then I search for "Event"
      and Should be 1 collection results
      and Should be filter checkboxes  All (1)  Evänt (1)  Süper (1)


Scenario: Search filter
    Given I've got a site with a collection
      and my collection has a collection search
      and my collection has a collection filter
      and I'm viewing the collection
    When I search for "Document"
    Then should be 1 collection results
      and Should be filter checkboxes  All (1)  Dokumänt (1)  Süper (1)

    When I search for "& - * $"
    Then page should not contain  error

    # Searching for query keywords (https://github.com/collective/collective.collectionfilter/issues/85)
    When I search for "and Document"
    Then should be 1 collection results
      and Should be filter checkboxes  All (1)  Dokumänt (1)  Süper (1)
    When I search for "or Document"
    Then should be 0 collection results
      and I should see 0 filter options on the page
    When I search for "not Document"
    Then should be 0 collection results
      and I should see 0 filter options on the page
