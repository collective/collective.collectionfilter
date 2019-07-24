
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***

${COLLECTION_NAME}  testcollection


*** Test Cases ***************************************************************

Scenario: Add filter tiles to page for collection

    Log in as site owner
    Go to  ${PLONE_URL}/testdoc

    # Setup Mosaic display and open editor
    Click element  css=#plone-contentmenu-display
    Click element  css=#plone-contentmenu-display-layout_view
    Go to  ${PLONE_URL}/testdoc/edit
    Wait Until Element Is Visible  css=.mosaic-select-layout
    Wait until Page contains element  jquery=a[data-value="default/basic.html"]
    Click element  jquery=a[data-value="default/basic.html"]
    Capture Page Screenshot  _screenshots/default-page.png

    # Enable mosaic layout editing
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.mosaic-button-layout
    Element should be visible  css=.mosaic-button-customizelayout
    Click element  css=.mosaic-button-customizelayout

    Add filter tile  ${COLLECTION_NAME}  Subject  checkboxes_dropdowns
    Add search tile  ${COLLECTION_NAME}

    # Save changes
    Wait Until Element Is Visible  css=.mosaic-button-save
    Click button  css=.mosaic-button-save
    Wait until page contains  Changes saved
    Go to  ${PLONE_URL}/testdoc
    Capture Page screenshot

    # Check clicking collection filter filters collection
    Select from List by value  xpath=//*[@class = 'filterContent']//select  Dokumänt
    Should be 2 collection results
    Capture Page Screenshot

    # Check colleciton search filters collection
    Go to  ${PLONE_URL}/testdoc
    Input text  css=.collectionSearch input[name='SearchableText']  Document
    Click Element  css=.collectionSearch button[type='submit']
    Should be 1 collection results
    Capture Page Screenshot