
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: Add filter portlets to collection

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

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
    Should be 3 filter checkboxes

    # the following doesn't work ... I think no 'keyup' event is fired
    # Clear element text  css=.collectionSearch input[name='SearchableText']
    # Should be 2 collection results
    # Should be 4 filter checkboxes


Scenario: Test Batching

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

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

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Manage portlets
    Add filter portlet  author_name  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results

    Should be 1 filter checkboxes

    Manage portlets
    Set Hide "author_name"
    Should be 0 filter checkboxes


