
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  View Test Collection
Test Teardown  Close all browsers




*** Test Cases ***************************************************************

Scenario: Add filter portlets to collection

    Manage portlets
    Add search portlet
    Add filter portlet  Subject  or  checkboxes_dropdowns

    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results

    Click Input "Dokumänt (2)"
    Should be 2 collection results

    Click Input "All (3)"
    Should be 3 collection results

    # TODO: Restore this to partial quicksearch test only for ajaxLoad scenarios and Plone > 5.0
    Input text with placeholder  Search  Document
    Click Button with text  Search  pos=2
    Should be 1 collection results

    # check for filtered subject checkbox list
    Should be 3 filter options

    # the following doesn't work ... I think no 'keyup' event is fired
    # Clear element text  css=.collectionSearch input[name='SearchableText']
    # Should be 2 collection results
    # Should be 4 filter options


Scenario: Test Batching

    Manage portlets
    Add filter portlet  Subject  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results

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

    Should be 3 collection results
    Should be 1 filter options

    Manage portlets
    Set portlet "author_name" "Hide if empty"
    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results
    # No idea why intermittently we get 1 filter option below instead of 0
    log source
    capture page screenshot
    Should be 0 filter options


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
     Then Should be 2 filter options
