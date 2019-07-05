
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: Add filter portlets to collection

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Click link  link:Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click link  link:Right column

    Add search portlet
    Add filter portlet  Subject  or  checkboxes_dropdowns

    Go to  ${PLONE_URL}/testcollection
    Xpath should match X times  //article[@class='entry']  3

    Click element  css=li.filter-dokumant.checkbox input
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  2

    Click element  css=li.filter-all.checkbox input
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  3

    Input text  css=.collectionSearch input[name='SearchableText']  Docu
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  1
    # check for filtered subject checkbox list
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]  3

    # the following doesn't work ... I think no 'keyup' event is fired
    #Clear element text  css=.collectionSearch input[name='SearchableText']
    #Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  2
    #Wait until keyword succeeds  5s  1s  Xpath should match X times  //div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]  4


Scenario: Test Batching

    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

    Click element  link=Manage portlets
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click element  partial link=Right

    Add filter portlet  Subject  or  checkboxes_dropdowns
    Go to  ${PLONE_URL}/testcollection
    Xpath should match X times  //article[@class='entry']  3

    Set Batch Size  1

    Xpath should match X times  //article[@class='entry']  1

    Click element  css=li.filter-super.checkbox input
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  1

    capture page screenshot
    Xpath should match X times  //nav[@class='pagination']//a  2

    Click element  xpath=//nav[@class='pagination']//a[1]
    Wait until keyword succeeds  5s  1s  Xpath should match X times  //article[@class='entry']  1
    capture page screenshot

    Xpath should match X times  //nav[@class='pagination']//a  2

    ${loc}=  get location
    should contain  ${loc}  collectionfilter=1
