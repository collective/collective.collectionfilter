
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  View Test Collection
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: Add filter portlets to collection

    Manage portlets
    Add search portlet
    Add filter portlet  Subject  or  checkboxes_dropdowns

    Go to  ${PLONE_URL}/testcollection
    Should be 6 collection results

    Click Input "Dokumänt (2)"
    Should be 2 collection results

    Click Input "All (6)"
    Should be 6 collection results

Scenario: Test Batching

    Manage portlets
    Add filter portlet  Subject  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection
    Should be 6 collection results

    Set Batch Size  1

    Should be 1 collection results

    Click Input "Süper (2)"
    Should be 1 collection results
    Should be 1 pages

    Click Page "1"
    Should be 1 collection results
    Should be 1 pages

    ${loc}=  get location
    should contain  ${loc}  collectionfilter=1

Scenario: Hide when no options

    Manage portlets
    Add filter portlet  author_name  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection

    Should be 6 collection results
    Should be 1 filter options

    Manage portlets
    Set portlet "author_name" "Hide if empty"
    Go to  ${PLONE_URL}/testcollection
    # No idea why intermittently we get 1 filter option below instead of 0
    log source
    capture page screenshot
    Should be 0 filter options
    Should be 6 collection results


Scenario: show hidden filter if just narrowed down

    Given Manage portlets
      and Add filter portlet  Type  single  checkboxes_dropdowns
      and Set portlet "Type" "Narrow down filter options"
      and Go to  ${PLONE_URL}/testcollection
      and Should be 3 filter options

      and Select Filter Option "Event (1)"
      and Should be 2 filter options

     When Manage portlets
      and Set portlet "Type" "Hide if empty"
      and Go to  ${PLONE_URL}/testcollection
      and Should be 3 filter options

    # But if we filter it down it shouldn't disappear as then we have no way to click "All" to get back
      and Select Filter Option "Event (1)"
      Log source
      capture page screenshot
     Then Should be 2 filter options


Scenario: Displaying multiple collection filters on a single page
    Given I've got a site with a collection
      and my collection has a collection filter portlet
      and my collection has a collection filter portlet  group_by=portal_type
    When I'm viewing the collection
    Then I should have a portlet titled "Subject" with 4 filter options
      and I should have a portlet titled "portal_type" with 3 filter options

Scenario: Add a section filter to a collection
  Given I've got a site with a collection
      and my collection has a collection section portlet
  When I'm viewing the collection
  Then I should have a portlet titled "My Section Filter" with 3 filter options