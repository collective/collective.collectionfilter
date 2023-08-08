
*** Settings *****************************************************************

Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/mosaic/tests/robot/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  OperatingSystem
Library  Collections  # needed for "Append To List"

*** Variables ***

${BROWSER}  Chrome

*** Keywords *****************************************************************

Default Setup
    Run Keyword  Plone test setup
    ${USE_TILES}=  Get Environment Variable   ROBOT_USE_TILES  default=${False}
    ${USE_TILES}=  Set Test Variable   ${USE_TILES}
    ${AJAX_ENABLED}=  Get Environment Variable   ROBOT_AJAX_ENABLED  default=${False}
    ${AJAX_ENABLED}=  Set Test Variable   ${AJAX_ENABLED}

Default Teardown
    run keyword if Test Failed  Capture Page Screenshot
    run keyword if Test Failed  Log Source
    run keyword if Test Failed  Log Variables
    Run Keyword  Plone test teardown

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
  Wait For Then Click Element  Log in


# --- THEN -------------------------------------------------------------------

I am logged in
  Wait until page contains  You are now logged in
  Page should contain  You are now logged in


# --- MISC

View Test Collection
    Open test browser
    Log in as site owner
    Go to  ${PLONE_URL}/testcollection

Run Keyword by label
    [Arguments]  ${label}   ${keyword}    @{args}
    # Possible to get 2 mosaic overlays with the same labels on page at once
    ${xpath}=   set variable  //*[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for and not(ancestor::div[contains(@class, 'mosaic-overlay')])]
    run keyword  ${keyword}  xpath=${xpath}  @{args}

Click Input "${label}"
    Wait for then click element  xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]

Select InAndOut
    [Arguments]  ${label}  @{values}
    Wait until page contains element  xpath=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']
    ${id}=  Get Element Attribute  xpath=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']  for
    FOR  ${value}  IN  @{values}
        Select from List by value  css=select#${id}-from  ${value}
        Click element  css=#${id} button[name='from2toButton']
    END


Select single select2
    [Arguments]  ${locator}  ${value}
    Wait for then click element  ${locator}
    Wait for then click Element  xpath=//div[contains(@class,'select2-result-label') and text() = '${value}']


Select multi select2
    [Arguments]  ${locator}  @{values}
    FOR  ${value}  IN  @{values}
        # open select2 dropdown
        Wait for then click element  ${locator}
        # click element
        Wait for then click element  xpath=//div[contains(@class,'select2-result-label') and text() = '${value}']
    END

select multi select2 with label
    [Arguments]  ${label}  @{values}
    # select2 don't have proper labels because the @for doesn't match an id of anything
    ${xpath}=   set variable  //label[normalize-space(text()) ='${label}']/following-sibling::div[contains(@class,'select2-container')]
    Wait until page contains element  xpath=${xpath}
    Select multi select2  xpath=${xpath}  @{values}


Click Button with text
    [Arguments]  ${text}  ${pos}=1
    Wait for then click element  xpath=(//*[@type="submit" and (normalize-space(@value)='${text}' or normalize-space(text())='${text}')])[${pos}]

Select Filter Option "${text}"
    select from list by label  xpath=//div[contains(@class, 'filterContent')]//select  ${text}

Input text with placeholder
    [Arguments ]  ${placeholder}  ${text}  ${pos}=1
    Input text  xpath=(//input[@placeholder='${placeholder}'])[${pos}]  ${text}

Manage Portlets
    Wait for then click element  link=Manage portlets
    Wait for element  xpath=//a[@id="portlet-manager-plone.rightcolumn"]
    Click link  xpath=//a[@id="portlet-manager-plone.rightcolumn"]

Select related filter collection
    Click element  css=div.pattern-relateditems-container input.select2-input
    Wait until page contains element  partial link=Test Collection
    Click element  partial link=Test Collection

Set Options
    [Arguments]  @{options}
    FOR    ${option}    IN    @{options}
        Click Input "${option}"
    END

# ---- CF stuff

Add search portlet
    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Search
    Wait for element  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Searchable Text
    #Select related filter collection
    Click element  css=.modal-footer button#form-buttons-add
    Wait until page contains element  xpath=//div[@class='portletAssignment']//a[text()='Searchable Text']


Add filter portlet
    [Arguments]   ${group_criteria}  ${filter_type}  ${input_type}  @{options}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter
    Wait for element  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${group_criteria}
    #Select related filter collection
    Set Filter Options  ${group_criteria}  ${filter_type}  ${input_type}  @{options}
    # Select from List by value  css=select#form-widgets-group_by  ${group_criteria}
    # Click Input "Show count"
    # Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    # Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.modal-footer button#form-buttons-add
    ${xpath}=  set variable  //div[contains(@class, 'portletAssignment')]//a[text()='${group_criteria}']
    Wait until page contains element  xpath=${xpath}


Set Filter Options
    [Arguments]   ${group_by}  ${filter_type}  ${input_type}  @{options}

    Run Keyword by label  Group by     Select from List by value  ${group_by}
    Run Keyword by label  Filter Type  Select from List by value  ${filter_type}
    Run Keyword by label  Input Type   Select from List by value  ${input_type}
    Set Options  @{options}
    Click Input "Show count"


Add sorting portlet
    [Arguments]   ${sort_on}  ${input_type}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter Result Sorting
    Wait for element  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Sort on

    Set Sorting Options  ${sort_on}  ${input_type}

    Click element  css=.modal-footer button#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignment')]//a[text()='Sort on']


Set sorting Options
    [Arguments]   ${sort_on}  ${input_type}
    #Run keyword by label  Enabled sort indexes  select multi select2    ${sort_on}
    select multi select2 with label  Enabled sort indexes  ${sort_on}
    Run Keyword by label  Input Type   Select from List by value   ${input_type}


Add Info portlet
    [Arguments]   ${header}  @{templates}  ${hide_when}=${None}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter Search Info
    Wait for element  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${header}
    Set Info Settings  form-widgets  @{templates}  hide_when=${hide_when}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${header}']



Should be ${X} filter options
    Sleep  0.5
    Page Should Contain Element  xpath=//div[contains(@class, 'filterContent')]//*[contains(@class, 'filterItem')]  limit=${X}

Should be filter options
    [Arguments]  @{values}
    Sleep  0.5
    List Labels Should Equal  xpath=//div[contains(@class, 'filterContent')]//select  @{values}

Should be filter checkboxes
    [Arguments]  @{values}
    Sleep  0.5
    Labels Should Equal  xpath=//div[contains(@class, 'filterContent')]//span[@class='filterLabel']  @{values}

List Labels Should Equal
   [Arguments]  ${selector}  @{expect}
   @{options}=  get list items  ${selector}
   Should Be Equal  ${expect}  ${options}

Labels Should Equal
    [Arguments]  ${selector}  @{expect}
    @{locators}=     Get Webelements    ${selector}
    ${result}=       Create List
    FOR   ${locator}   IN    @{locators}
           ${name}=    Get Text    ${locator}
           Append To List  ${result}  ${name}
    END

    # USE_TILES differs from order
    sort list  ${expect}
    sort list  ${result}

    Should Be Equal  ${expect}  ${result}

Should be ${X} collection results
    # Wait for element  css=#content-core
    # below should work for both collections and contentlisting tiles
    ${xpath}=  Set Variable if  ${USE_TILES}  //span[@class='summary']  //div[@class='entries']/article
    Run keyword if  ${X}>0  Wait For Elements  xpath=${xpath}
    Sleep  0.5
    ${count} =  Get Element Count  xpath=${xpath}
    Should Be Equal as Numbers  ${count}  ${X}

Should be ${X} pages
    ${X}=  evaluate  ${X} + 1  # need we have next or previous
    Page Should Contain Element  xpath=//ul[@class='pagination']//a  limit=${X}

Should be Info with text: ${text}
    wait until element contains  css=.filterInfoContent  ${text}

# TODO: there is a bug where the aside.collectionInfo is still visible on screen.
Should be no Info
    wait until element is not visible  css=.filterInfoContent

# Set portlet "${title}" "${checkbox}"
#     Click Link  ${title}
#     Click Input "${checkbox}"
#     Click element  css=.plone-modal-footer input#form-buttons-apply
#     Wait until page does not contain element  css=.plone-modal-dialog

Click Page "${page}"
    Click element  xpath=//ul[@class='pagination']//a[${page}]

Ajax has completed
    Wait For Condition	return jQuery.active == 0  timeout=5 sec

# --- Setup -------------------------------------------------------------------
I've got a site with a collection
    [arguments]  ${batch}=20
    Log in as site owner
    run keyword if  ${USE_TILES}   Enable mosaic layout for page  ${PLONE_URL}/testdoc  batch=${batch}
    run keyword if  ${USE_TILES}==False   Go to  ${PLONE_URL}/testcollection
    run keyword if  ${USE_TILES}==False   Set Batch Size  ${batch}

I've got a site without a listing
    I've got a site with a collection  0

My collection has a collection search
    run keyword if  ${USE_TILES}  My collection has a collection search tile
    run keyword if  ${USE_TILES}==False  My collection has a collection search portlet

My collection has a collection filter
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns  @{options}
    run keyword if  ${USE_TILES}  My collection has a collection filter tile  ${group_by}  ${op}  ${style}  @{options}
    run keyword if  ${USE_TILES}==False  My collection has a collection filter portlet  ${group_by}  ${op}  ${style}  @{options}

My collection has a collection sorting
    [Arguments]  ${sort_on}=Sortable Title
    run keyword if  ${USE_TILES}  My collection has a collection sorting tile  ${sort_on}
    run keyword if  ${USE_TILES}==False  My collection has a collection sorting portlet  ${sort_on}

My collection has a collection info
    [Arguments]  ${header}="Current Filter"  @{templates}  ${hide_when}=${None}
    run keyword if  ${USE_TILES}  My collection has a collection info tile  ${header}   @{templates}  hide_when=${hide_when}
    run keyword if  ${USE_TILES}==False  My collection has a collection info portlet  ${header}   @{templates}  hide_when=${hide_when}

I'm viewing the collection
    run keyword if  ${USE_TILES}  Go to  ${PLONE_URL}/testdoc
    run keyword if  ${USE_TILES}==False  Go to  ${PLONE_URL}/testcollection
    # should be 6 items in result

My collection has a collection search portlet
    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add search portlet

My collection has a collection filter portlet
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns  @{options}

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add filter portlet  ${group_by}  ${op}  ${style}  @{options}

My collection has a collection sorting portlet
    [Arguments]  ${sort_on}=Sortable Title

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add sorting portlet  ${sort_on}  links

My collection has a collection info portlet
    [Arguments]  ${header}="Current Filter"  @{templates}  ${hide_when}=${None}

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add info portlet  ${header}   @{templates}  hide_when=${hide_when}

Set Batch Size
    [Arguments]   ${batch_size}
    run keyword if  ${USE_TILES}==False  Go to  ${PLONE_URL}/testcollection/edit
    run keyword if  ${USE_TILES}  Edit Listing Tile
    Run keyword by label  Item count  Input Text  ${batch_size}
    Run keyword if  ${USE_TILES}  Wait For Then Click Element  css=.pattern-modal-buttons #buttons-save
    Wait For Then Click Element  css=#form-buttons-save

Edit Listing Tile
    Go to  ${PLONE_URL}/testdoc/edit
    #Wait until page contains element  css=.mosaic-btn-delete
    #Wait until page contains element   css=#mosaic-panel
    Wait for element  css=.mosaic-toolbar
    #Unselect Frame
    #mouse over  css=.mosaic-plone.app.standardtiles.contentlisting-tile
    Wait For Then Click Element  css=.contentlisting-tile
    Edit Current Tile

# --- Core Functionality ------------------------------------------------------
I search for "${search}"
    Input text  css=.collectionSearch input[name='SearchableText']  ${search}
    Run keyword if  ${AJAX_ENABLED}==False and ${USE_TILES}==False  Wait for then click element  css=.collectionSearch button[type='submit']
    Run keyword if  ${AJAX_ENABLED}==True  Sleep  0.5

I should have a portlet titled "${filter_title}" with ${number_of_results} filter options
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and descendant-or-self::*[contains(text(), '${filter_title}')]]
    ${filter_item_xpath}  Convert to string  div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]

    Page Should Contain Element  xpath=//${portlet_title_xpath}
    Wait until keyword succeeds  2s  1s  Page Should Contain Element  xpath=//${portlet_title_xpath}/parent::*[contains(@class, 'collectionFilter')]//${filter_item_xpath}  limit=${number_of_results}

I should have a filter with ${number_of_results} options
    Page Should Contain Element  xpath=//aside[contains(@class,'collectionFilter') and count(.//div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')])=${number_of_results} ]  limit=1

I should see ${number} filter options on the page
    Page should contain element  xpath=//aside[contains(@class,'collectionFilter') ]//div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]  limit=${number}


I should not have a portlet titled "${filter_title}"
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and descendant-or-self::*[contains(text(), '${filter_title}')]]

    Page Should not Contain Element  xpath=//${portlet_title_xpath}


I should not see any results
    Wait until keyword succeeds  2s  1s  Element should be visible  xpath=//*[@id="content-core"]/*[text()="No results were found."]

I should have a portlet titled "${filter_title}" with text ${text}
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and contains(text(), '${filter_title}')]
    ${filter_item_xpath}  Convert to string  div[contains(@class, 'portletContent')]

    Page Should Contain Element  xpath=//${portlet_title_xpath}
    Wait Until Element Contains  xpath=//${portlet_title_xpath}/parent::*[contains(@class, 'collectionFilterInfo')]//${filter_item_xpath}  ${text}

I sort by "${sort_on}"
    Wait for element   xpath=//span[contains(normalize-space(text()), '${sort_on}')]
    ${glyph}=  Get Element Attribute  xpath=//span[contains(normalize-space(text()), '${sort_on}')]//span  class
    Click Link  link=${sort on}
    Wait until element is not visible   xpath=//span[contains(normalize-space(text()), '${sort_on}')]//span[@class='${glyph}']

Results Are Sorted
    ${xpath}=    Set Variable if  ${USE_TILES}  //span[@class='summary']  //div[@class='entries']//a[contains(@class, 'url')]
    ${count}=    Get Element Count    xpath=${xpath}
    ${names}=    Create List
    FOR    ${i}    IN RANGE    1    ${count} + 1
        ${name}=    Get Text    xpath=(${xpath})[${i}]
        Append To List    ${names}    ${i}${name}
    END

    ${sorted}=  copy list  ${names}  False
    sort list  ${sorted}
    log many  ${sorted}  ${names}
    run keyword if  $sorted!=$names   Fail   Results are not sorted ${sorted}!=${names}

# --- Tiles -------------------------------------------------------------------

Open advanced mosaic editor
    Go to  ${PLONE_URL}/testdoc/edit
    Wait for element  css=#content.mosaic-panel
    Execute javascript  $("#content.mosaic-panel").addClass("mosaic-advanced")
    Wait for element  css=.mosaic-advanced
    # d-index fix until fixed in mosaic
    Update element style  css=.mosaic-IDublinCore-description-tile  zIndex  unset

My collection has a collection filter tile
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns  @{options}
    Open advanced mosaic editor
    Add filter tile  ${group_by}  ${op}  ${style}  @{options}

My collection has a collection search tile
    Open advanced mosaic editor
    Add search tile

My collection has a collection info tile
    [Arguments]  ${header}  @{templates}  ${hide_when}=${None}
    Open advanced mosaic editor
    Add info tile  @{templates}  hide_when=${hide_when}

My collection has a collection sorting tile
    [Arguments]  ${sort_on}=Sortable Title
    Open advanced mosaic editor
    Insert Tile "Collection Result Listing Sort"
    Set Sorting Options  ${sort_on}  links
    # Run Keyword by label  Content Selector  Input Text  .contentlisting-tile
    Click element  css=.pattern-modal-buttons #buttons-save
    Drag tile

Enable mosaic layout for page
    [Arguments]  ${page}=${PLONE_URL}/testdoc  ${batch}=20

    go to  ${page}
    # Setup Mosaic display and open editor
    Wait for then click element  link=Display
    Wait for then click Element  css=#plone-contentmenu-display-layout_view
    Go to  ${page}/edit

    # Create default layout if its a Page
    Wait for element  xpath=//a[@data-value='default/basic.html']
    Execute javascript  $("[data-value='default/basic.html']").trigger("click");

    # Enable layout editing
    Wait for then click element  css=.mosaic-button-layout
    Wait for then click element  css=.mosaic-button-customizelayout

    # Add a embed content tile pointing to the collection
    #Add existing content tile  /testdoc
    run keyword if  ${batch}>0  Add contentlisting tile  ${batch}

    Save mosaic page

Edit mosaic page
    [Arguments]  ${page}=${PLONE_URL}/testdoc
    Go to  ${page}/edit
    Wait for element  css=.mosaic-toolbar

Save mosaic page
    Wait for then Click Element  css=.mosaic-button-save
    Wait until page contains  Changes saved


Add filter tile
    [Arguments]   ${group_by}  ${filter_type}  ${input_type}  @{options}

    Insert Tile "Collection Filter"
    Drag tile
    Edit Current Tile

    Set Filter Options  ${group_by}  ${filter_type}  ${input_type}  @{options}
    # Run Keyword by label  Content Selector  Input Text  .contentlisting-tile

    Click element  css=.pattern-modal-buttons #buttons-save


Add search tile
    [Arguments]   ${collection_name}=${None}

    Insert tile "Collection Search"
    Drag tile
    Edit Current Tile
    run keyword if  $collection_name!=${None}  set relateditem  formfield-collective-collectionfilter-tiles-search-target_collection  ${collection_name}
    # Run Keyword by label  Content Selector  Input Text  .contentlisting-tile

    Click element  css=.pattern-modal-buttons #buttons-save


Add info tile
    [Arguments]   @{templates}  ${hide_when}=${None}  ${collection_name}=${None}

    Insert tile "Collection Filter Info"
    run keyword if  $collection_name!=${None}  set relateditem  formfield-collective-collectionfilter-tiles-info-target_collection  ${collection_name}
    # Complete filter form
    Set Info Settings  collective-collectionfilter-tiles-info  @{templates}  hide_when=${hide_when}
    # Run Keyword by label  Content Selector  Input Text  .contentlisting-tile

    Click element  css=.pattern-modal-buttons #buttons-save
    Drag tile


Set Info Settings
    [Arguments]   ${prefix}  @{templates}  ${hide_when}

    select multi select2 with label  Template Type  @{templates}
    run keyword if  $hide_when  Run Keyword  select multi select2 with label  Hide when  ${hide_when}



Add existing content tile
    [Arguments]   ${collection_name}=${None}

    Insert tile "Existing Content"
    run keyword unless  $collection_name  set relateditem  formfield-plone-app-standardtiles-existingcontent-content_uid    ${collection_name}
    Click element  css=.pattern-modal-buttons #buttons-save

    Drag tile

Add contentlisting tile
    [Arguments]  ${batch}=20
    Insert tile "Content listing"
    Drag tile
    Edit Current Tile

    # set path criteria depth to unlimited
    #Select from list by value  css=select.querystring-criteria-depth  -1

    # Since we aren't using the collection we need to recreate the same settings clickin on select2
    Wait for element  link=Select criteria
    Select single select2  xpath=(//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-index'])[2]/div  Type
    Select multi select2  xpath=(//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-value'])[2]/div  Event  Page

    Run Keyword by label  Item count   Input Text  ${batch}

    Capture Page Screenshot
    Wait for then click element  css=.pattern-modal-buttons #buttons-save

Edit Current Tile
    Wait For Then Click Element  css=.mosaic-selected-tile .mosaic-btn-settings


Drag tile
    Wait for element  css=.mosaic-helper-tile-new
    Update element style  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom  display  block
    Wait for element  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom
    Mouse over  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom
    Wait for then click element  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom

Filter by
    [Arguments]  ${filter}
    Wait for element  css=.filterContent
    Select from List by value  xpath=//div[@class = 'filterContent']//select  ${filter}

# TODO: doesn't work yet
Set relateditem
    [Arguments]  ${id}  ${path}
    Wait for then click element  xpath=//div[@id='${id}']//ul[@class='select2-choices']
    Wait for then click element  xpath=//div[@id='select2-drop']//a[.//text() = '${path}']

Insert Tile "${name}"
    Wait for then click element  css=.mosaic-toolbar .select2-container.mosaic-menu-insert a
    Wait for then click element  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "${name}"]
