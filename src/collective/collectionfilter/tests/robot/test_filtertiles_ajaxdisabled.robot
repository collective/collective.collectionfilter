
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

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
    # Broken when running with AJAX enabled
    Go to  ${TEST_PAGE}
    Filter by  Dokumänt
    Should be 2 collection results
    Capture Page Screenshot
    
    # Check collection search filters collections
    Given go to  ${TEST_PAGE}
    When I search for Document and click search
    Then should be 4 collection results
      and Capture Page Screenshot

    Given Go to  ${TEST_PAGE}
    When I search for ${EMPTY} and click search
    Then should be 6 collection results
