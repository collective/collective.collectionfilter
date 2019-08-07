
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


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

    Input text  css=.collectionSearch input[name='SearchableText']  Document
    # Text input is reloaded live ... wait a bit
    Should be 1 collection results

    # check for filtered subject checkbox list
    Should be 3 filter checkboxes

    # the following doesn't work ... I think no 'keyup' event is fired
    #Input text  css=.collectionSearch input[name='SearchableText']
    #Should be 2 collection results
    #Should be 4 filter checkboxes


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
