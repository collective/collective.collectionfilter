
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***
${collection_page}  ${PLONE_URL}/testcollection


*** Test Cases ***************************************************************

Scenario: Add filter portlets to collection

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Click element  link=Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click element  partial link=Right

    Add search portlet
    Add filter portlet  Subject  or  checkboxes_dropdowns

    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results

    Click element  css=li.filter-dokumant.checkbox input
    Should be 2 collection results

    Capture Page Screenshot
    Click element  css=li.filter-all.checkbox input
    Should be 3 collection results

    # TODO: Restore this to partial quicksearch test only for ajaxLoad scenarios and Plone > 5.0
    Input text  css=.collectionSearch input[name='SearchableText']  Document
    Click Element  css=.collectionSearch button[type='submit']
    Should be 1 collection results

    # check for filtered subject checkbox list
    Should be 3 filter checkboxes

    # the following doesn't work ... I think no 'keyup' event is fired
    # Clear element text  css=.collectionSearch input[name='SearchableText']
    # Should be 2 collection results
    # Should be 4 filter checkboxes


Scenario: Add section filter portlet to collection
    Log in as site owner
    Go to  ${collection_page}

    Click element  link=Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click element  partial link=Right

    Add section filter portlet

    # Check home displays correct number of folders and all results
    Go to  ${collection_page}
    Capture Page Screenshot
    Section filter should be hidden  Test Folder3
    Should be 3 section results
    Should be 6 collection results
    
    # Check opening a folder with a single document shows one result
    Click section filter  Test Folder2
    Capture Page Screenshot
    Should be 2 section results
    Should be 1 collection results
    Click section filter  Home

    # Check sub-folders and their contents are correctly shown
    Click section filter  Test Folder
    Capture Page Screenshot
    # Intermittent bug causing non-existent section to show
    # Should be 3 section results
    Should be 2 collection results

    Click section filter  Test Sub-Folder
    Should be 3 section results
    Should be 1 collection results

    # Check returning to home returns all collection results
    Click section filter  Home
    Should be 3 section results
    Should be 6 collection results


Scenario: Test Batching

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Click element  link=Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click element  partial link=Right

    Add filter portlet  Subject  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results

    Set Batch Size  1

    Should be 1 collection results

    Click element  css=li.filter-super.checkbox input
    Should be 1 collection results
    Should be 1 pages

    Click element  xpath=//nav[@class='pagination']//a[1]
    Should be 1 collection results
    Should be 1 pages

    ${loc}=  get location
    should contain  ${loc}  collectionfilter=1
