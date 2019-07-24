
*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  Selenium2Screenshots/keywords.robot

*** Variables ***

${BROWSER}  chrome


*** Keywords *****************************************************************


# --- Given ------------------------------------------------------------------

a login form
  Go To  ${PLONE_URL}/login_form
  Wait until page contains  Login Name
  Wait until page contains  Password

a logged-in manager
    Enable autologin as  Manager
    Set autologin username  Manager


# --- WHEN -------------------------------------------------------------------

I enter valid credentials
  Input Text  __ac_name  admin
  Input Text  __ac_password  secret
  Click Button  Log in


# --- THEN -------------------------------------------------------------------

I am logged in
  Wait until page contains  You are now logged in
  Page should contain  You are now logged in


# --- MISC

Select related filter collection
    Click element  css=div.pattern-relateditems-container input.select2-input
    Wait until page contains element  partial link=Test Collection
    Click element  partial link=Test Collection

Add search portlet
    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Search
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Searchable Text
    #Select related filter collection
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[@class='portletAssignments']//a[text()='Searchable Text']

Add filter portlet
    [Arguments]   ${group_criteria}  ${filter_type}  ${input_type}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${group_criteria}
    #Select related filter collection
    Select from List by value  css=select#form-widgets-group_by  ${group_criteria}
    Click element  css=input#form-widgets-show_count-0
    Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Capture Page Screenshot
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${group_criteria}']


Should be ${X} filter checkboxes
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]  limit=${X}

Should be ${X} collection results
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//article[@class='entry']  limit=${X}

Should be ${X} pages
    ${X}=  evaluate  ${X} + 1  # need we have next or previous
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//nav[@class='pagination']//a  limit=${X}

Set Batch Size
    [Arguments]   ${batch_size}

    Go to  ${PLONE_URL}/testcollection/edit
    Input text  css=input#form-widgets-ICollection-item_count  ${batch_size}
    Click element  css=input#form-buttons-save
    Go to  ${PLONE_URL}/testcollection


# --- Tiles -------------------------------------------------------------------
Add filter tile
    [Arguments]   ${collection_name}  ${filter_type}  ${input_type}

    # Insert content filter
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.select2-container.mosaic-menu-insert a
    Wait until element is visible  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Filter"]
    Click element  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Filter"]

    # Complete filter form
    Wait until element is visible  css=.plone-modal-content
    Input text  css=#collective-collectionfilter-tiles-filter-header  ${collection_name}
    Click element  xpath=//div[@id='formfield-collective-collectionfilter-tiles-filter-target_collection']//ul[@class='select2-choices']
    Wait until element is visible  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Click element  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Click element  css=#collective-collectionfilter-tiles-filter-group_by
    Select from List by value  css=select#collective-collectionfilter-tiles-filter-group_by  ${filter_type}
    Select from List by value  css=select#collective-collectionfilter-tiles-filter-input_type  ${input_type}
    Click element  css=.pattern-modal-buttons #buttons-save

    # Drag tile into place
    Wait until page contains element  css=.mosaic-helper-tile-new
    Wait until element is visible  css=.mosaic-helper-tile-new
    Update element style  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom  display  block
    Mouse over  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom
    Click element  css=.mosaic-selected-divider

    # Save changes
    Wait Until Element Is Visible  css=.mosaic-button-save
    Click button  css=.mosaic-button-save
    Wait until page contains  Changes saved