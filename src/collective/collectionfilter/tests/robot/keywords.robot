
*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  Selenium2Screenshots/keywords.robot

*** Variables ***

${BROWSER}  chrome


*** Keywords *****************************************************************

Default Teardown
    Run Keyword If Test Failed        Capture Page Screenshot
    Close all browsers

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

View Test Collection
    Open test browser
    Log in as site owner
    Go to  ${PLONE_URL}/testcollection


Click Input "${label}"
    Wait until page contains element  xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]
    Click Element  xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]

Click Button with text
    [Arguments]  ${text}  ${pos}=1
    Wait until page contains element  xpath=(//*[@type="submit" and (normalize-space(@value)='${text}' or normalize-space(text())='${text}')])[${pos}]
    Click Element  xpath=(//*[@type="submit" and (normalize-space(@value)='${text}' or normalize-space(text())='${text}')])[${pos}]

Select Filter Option "${text}"
    select from list by label  xpath=//div[contains(@class, 'filterContent')]//select  ${text}

Input text with placeholder
    [Arguments ]  ${placeholder}  ${text}  ${pos}=1
    Input text  xpath=(//input[@placeholder='${placeholder}'])[${pos}]  ${text}

Manage Portlets
    Click element  link=Manage portlets
    # Sometimes the click opens the backup page instead of the popup menu
    ${present}=  Run Keyword And Return Status    Element Should Be Visible   partial link=Right
    Run Keyword If    ${present}    Click element  partial link=Right
    

Select related filter collection
    Click element  css=div.pattern-relateditems-container input.select2-input
    Wait until page contains element  partial link=Test Collection
    Click element  partial link=Test Collection

Add search portlet
    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Search
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Searchable Text
    Input text  css=input#form-widgets-button_text  Click to search
    Input text  css=input#form-widgets-placeholder  Enter some keyword
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
    Click Input "Show count"
    Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${group_criteria}']

Add sorting portlet
    [Arguments]   ${sort_on}  ${input_type}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter Result Sorting
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Sort on
    Select from List by value  css=select#form-widgets-sort_on-from  ${sort_on}
    Click element  css=#form-widgets-sort_on button[name='from2toButton']
    Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='Sort on']


Should be ${X} filter options
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//div[contains(@class, 'filterContent')]//*[contains(@class, 'filterItem')]  limit=${X}

Should be ${X} collection results
    Wait until element is visible  css=#content-core
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

Set portlet "${title}" "${checkbox}"
    Click Link  ${title}
    Click Input "${checkbox}"
    Click element  css=.plone-modal-footer input#form-buttons-apply
    Wait until page does not contain element  css=.plone-modal-dialog

Click Page "${page}"
    Click element  xpath=//nav[@class='pagination']//a[${page}]

Ajax has completed
    Wait For Condition	return jQuery.active == 0  timeout=5 sec

# --- Setup -------------------------------------------------------------------
I've got a site with a collection
    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

My collection has a collection search portlet
    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add search portlet

My collection has a collection filter portlet
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add filter portlet  ${group_by}  ${op}  ${style}

My collection has a collection sorting portlet
    [Arguments]  ${sort_on}=sortable_title

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add sorting portlet  ${sort_on}  links

I'm viewing the collection
    Go to  ${PLONE_URL}/testcollection
    Should be 3 collection results
    
I should see the search portlet placeholder displays the text "${placeholder_text}"
    Wait Until Element Is Visible  xpath=//input[@name='SearchableText' and @placeholder='${placeholder_text}']

I should see the search portlet search button displays the text "${button_text}"
    Wait Until Element Is Visible  xpath=//button[@type='submit' and text()='${button_text}']

# --- Core Functionality ------------------------------------------------------
I search for "${search}" with ajax
    Wait until element is not visible  css=.collectionSearch button[type='submit']  timeout=5 sec
    Input text  css=.collectionSearch input[name='SearchableText']  ${search}
    Wait until keyword succeeds  5s  1s  Ajax has completed

I search for "${search}" and click search
    Wait until element is visible  css=.collectionSearch button[type='submit']
    Input text  css=.collectionSearch input[name='SearchableText']  ${search}
    Click Element  css=.collectionSearch button[type='submit']

I search for "${search}"
    Input text  css=.collectionSearch input[name='SearchableText']  ${search}
    ${present}=  Run Keyword And Return Status   Element Should Be Visible  css=.collectionSearch button[type='submit']
    Run Keyword If    ${present}   Click Element  css=.collectionSearch button[type='submit']

I should have a portlet titled "${filter_title}" with ${number_of_results} filter options
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and descendant-or-self::*[contains(text(), '${filter_title}')]]
    ${filter_item_xpath}  Convert to string  div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]

    Page Should Contain Element  xpath=//${portlet_title_xpath}
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//${portlet_title_xpath}/parent::*[contains(@class, 'collectionFilter')]//${filter_item_xpath}  limit=${number_of_results}

I should not have a portlet titled "${filter_title}"
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and descendant-or-self::*[contains(text(), '${filter_title}')]]

    Page Should not Contain Element  xpath=//${portlet_title_xpath}


I should not see any results
    Sleep  1 sec
    Element should be visible  xpath=//*[@id="content-core"]/*[text()="No results were found."]

I sort by "${sort_on}"
    Wait until element is visible  css=.collectionSortOn

    Click Element  css=.collectionSortOn .sortItem .${sort_on}
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  css=.collectionSortOn .sortItem.selected .${sort_on} span.glyphicon-sort-by-attributes

    Click Element  css=.collectionSortOn .sortItem .${sort_on}
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  css=.collectionSortOn .sortItem.selected .${sort_on} span.glyphicon-sort-by-attributes-alt

should be no errors


# --- Tiles -------------------------------------------------------------------
Enable mosaic layout for page
    [Arguments]  ${page}

    # Setup Mosaic display and open editor
    Click element  link=Display
    Wait Until Element Is visible  css=#plone-contentmenu-display-layout_view
    Click element  link=Mosaic layout
    Go to  ${page}/edit

    # Create default layout
    Wait Until Element Is Visible  css=.mosaic-select-layout
    Wait until Page contains element  xpath=//a[@data-value='default/basic.html']
    Click element  xpath=//a[@data-value='default/basic.html']

    # Enable layout editing
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.mosaic-button-layout
    Wait Until Element Is visible  css=.mosaic-button-customizelayout
    Click element  css=.mosaic-button-customizelayout

    Save mosaic page

Save mosaic page
    Wait Until Element Is Visible  css=.mosaic-button-save   timeout=5 sec
    Click button  css=.mosaic-button-save
    Wait until page contains  Changes saved   timeout=10 sec

Add filter tile
    [Arguments]   ${collection_name}  ${filter_type}  ${input_type}

    # Insert content filter
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.select2-container.mosaic-menu-insert a
    Wait until element is visible  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Filter"]
    Click element  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Filter"]

    # Complete filter form
    Wait until element is visible  xpath=//div[@class='plone-modal-dialog' and .//*[contains(text(), 'Collection')]]
    Click element  xpath=//div[@id='formfield-collective-collectionfilter-tiles-filter-target_collection']//ul[@class='select2-choices']
    Wait until element is visible  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Click element  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Select from List by value  css=select#collective-collectionfilter-tiles-filter-group_by  ${filter_type}
    Select from List by value  css=select#collective-collectionfilter-tiles-filter-input_type  ${input_type}
    Click element  css=.pattern-modal-buttons #buttons-save

    Drag tile

Add search tile
    [Arguments]   ${collection_name}

    # Insert collection search
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.select2-container.mosaic-menu-insert a
    Wait until element is visible  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Search"]
    Click element  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "Collection Search"]

    # Complete filter form
    Wait until element is visible  xpath=//div[@class='plone-modal-dialog' and .//*[contains(text(), 'Collection')]]
    Wait until element is visible  css=#collective-collectionfilter-tiles-search-header
    Click element  xpath=//div[@id='formfield-collective-collectionfilter-tiles-search-target_collection']//ul[@class='select2-choices']
    Wait until element is visible  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Click element  xpath=//div[@id='select2-drop']//a[.//text() = '/${collection_name}']
    Click element  css=.pattern-modal-buttons #buttons-save

    Drag tile

Drag tile
    Wait until page contains element  css=.mosaic-helper-tile-new
    Wait until element is visible  css=.mosaic-helper-tile-new
    Update element style  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom  display  block
    Mouse over  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom
    Click element  css=.mosaic-selected-divider

Filter by
    [Arguments]  ${filter}
    Wait until element is visible  css=.filterContent
    Select from List by value  xpath=//div[@class = 'filterContent']//select  ${filter}
