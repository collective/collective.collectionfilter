
*** Settings *****************************************************************

Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***

${COLLECTION_NAME}  testcollection
${TEST_PAGE}  ${PLONE_URL}/testdoc


*** Test Cases ***************************************************************

Scenario: Add filter tiles to page for collection

    Log in as site owner
    Go to  ${TEST_PAGE}

    # Setup full mosaic display and open editor
    Enable mosaic layout for page  ${TEST_PAGE}
    Capture Page Screenshot

    # Add tiles to page
    Go to  ${TEST_PAGE}/edit
    Add filter tile  ${COLLECTION_NAME}  Subject  checkboxes_dropdowns
    Add search tile  ${COLLECTION_NAME}
    Save mosaic page
    Go to  ${TEST_PAGE}
    Capture Page screenshot

    # Check collection filter filters collections
    Go to  ${TEST_PAGE}
    Filter by  Dokumänt
    Should be 2 collection results
    Capture Page Screenshot
    # Filtering by all with checkboxes_dropdowns without ajax results in no page change

    # Check collection search filters collections
    Go to  ${TEST_PAGE}
    Search for  Dokumänt
    Should be 1 collection results
    Capture Page Screenshot
    Go to  ${TEST_PAGE}
    Search for  ${EMPTY}
    Should be 3 collection results