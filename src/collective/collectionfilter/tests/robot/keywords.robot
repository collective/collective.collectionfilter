
*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  Selenium2Screenshots/keywords.robot
Library  OperatingSystem


*** Variables ***

${BROWSER}  chrome

*** Keywords *****************************************************************

Default Setup
# Not passed in as variable by robotsuite as variables collected before layer setup
    ${USE_TILES}=  Get Environment Variable   ROBOT_USE_TILES  default=${False}
    ${USE_TILES}=  Set Test Variable   ${USE_TILES}
    open test browser
    #Set Window Size  ${1400}  ${8000}

Default Teardown
    Run Keyword If Test Failed        Capture Page Screenshot
    Run Keyword If Test Failed        Log Source
#    Run Keyword If Test Failed        Log Variables
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

Run Keyword by label
    [Arguments]  ${label}   ${keyword}    @{args}
    # Possible to get 2 mosaic overlays with the same labels on page at once
    ${xpath}=   set variable  //*[ @id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for and not(ancestor::div[contains(@class, 'mosaic-overlay')])]
    Wait until page contains element  xpath=${xpath}
    run keyword  ${keyword}  xpath=${xpath}  @{args}

Click Input "${label}"
    Wait until page contains element  xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]
    Click Element  xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]

Select InAndOut
    [Arguments]  ${label}  @{values}
    Wait until page contains element  xpath=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']
    ${id}=  Get Element Attribute  xpath=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']  for
    :FOR  ${value}  IN  @{values}
    \    Select from List by value  css=select#${id}-from  ${value}
    \    Click element  css=#${id} button[name='from2toButton']


Select single select2  
    [Arguments]  ${locator}  ${value}
    ${select2}=  get webelement  ${locator}
    execute javascript  $(arguments[0]).select2("open")  ARGUMENTS  ${select2}
    wait until element is visible  css=.select2-result-label
    Click Element  xpath=//div[contains(@class,'select2-result-label') and text() = '${value}']

    #Click link  link=Select criteria
    #pause
    #select from list by label  xpath=(//div[@class='querystring-criteria-index'])[5]//select  Type
    #Click Element  xpath=(//div[@class='querystring-criteria-index'])[5]//*[@class='select2-arrow']//a
    # $($x("(//div[@class='querystring-criteria-index'])[5]/div")).select2("val", "portal_type").trigger("change")


Select multi select2
    [Arguments]  ${locator}  @{values}
    # select2-choices select2-search-field select2-input
    #select from list by label  xpath=(//select[@class='querystring-criteria-value-MultipleSelectionWidget'])[1]  Event
    #select from list by label  xpath=(//select[@class='querystring-criteria-value-MultipleSelectionWidget'])[1]  Page
    ${select2}=  get webelement  ${locator}
    execute javascript  $(arguments[0]).select2("val",arguments[1])  ARGUMENTS  ${select2}  ${values}
    :FOR  ${value}  IN  @{values} 
    # Hack to only find those in the tile popup up not the mosaic popup 
    #\    wait until element is visible  //*[contains(@class,'plone-modal ')]//li[@class='select2-search-choice']//*[contains(text(), '${value}')]
    \    Wait until keyword succeeds  5s  1s  call method  ${select2}  find_elements  by=xpath  value=.//li[@class='select2-search-choice']//*[contains(text(), '${value}')]

    # Click Element  xpath=(//div[@class='querystring-criteria-value'])[3]//input
    # wait until element is visible  css=.select2-result-label
    # Click Element  xpath=//div[contains(@class,'select2-result-label') and text() = 'Event']
    # Click Element  xpath=(//div[@class='querystring-criteria-value'])[3]//input
    # wait until element is visible  css=.select2-result-label
    # Click Element  xpath=//div[contains(@class,'select2-result-label') and text() = 'Page']

select multi select2 with label
    [Arguments]  ${label}  @{values}
    # select2 don't have proper labels because the @for doesn't match an id of anything
    ${xpath}=   set variable  //label[normalize-space(text()) ='${label}']/following-sibling::div[contains(@class,'select2-container')]
    Wait until page contains element  xpath=${xpath}
    run keyword   select multi select2  xpath=${xpath}  @{values}


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

Set Options 
    [Arguments]  @{options}
    FOR    ${option}    IN    @{options}
        Click Input "${option}"
    END

# ---- CF stuff

Add search portlet
    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Result Search
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Searchable Text
    #Select related filter collection
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[@class='portletAssignments']//a[text()='Searchable Text']

Add filter portlet
    [Arguments]   ${group_criteria}  ${filter_type}  ${input_type}  @{options}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Result Filter
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${group_criteria}
    #Select related filter collection
    Set Filter Options  ${group_criteria}  ${filter_type}  ${input_type}  @{options}
    # Select from List by value  css=select#form-widgets-group_by  ${group_criteria}
    # Click Input "Show count"
    # Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    # Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${group_criteria}']


Set Filter Options
    [Arguments]   ${group_by}  ${filter_type}  ${input_type}  @{options}

    Run Keyword by label  Filter by     Select from List by value  ${group_by}
    Run Keyword by label  Filter Type  Select from List by value  ${filter_type}
    Run Keyword by label  Input Type   Select from List by value   ${input_type}
    Set Options  @{options}
    Click Input "Show count"


Add sorting portlet
    [Arguments]   ${sort_on}  ${input_type}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Result Sort
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Sort on

    Set Sorting Options  ${sort_on}  ${input_type}

    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='Sort on']


Set sorting Options
    [Arguments]   ${sort_on}  ${input_type}
    #Run keyword by label  Enabled sort indexes  select multi select2    ${sort_on}
    select multi select2 with label  Enabled sort fields  ${sort_on}
    Run Keyword by label  Input Type   Select from List by value   ${input_type}


Add Info portlet
    [Arguments]   ${header}  @{templates}  ${hide_when}=${None}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet Result Filter Info
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${header}
    Set Info Settings  form-widgets  @{templates}  hide_when=${hide_when}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${header}']



Should be ${X} filter options
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//div[contains(@class, 'filterContent')]//*[contains(@class, 'filterItem')]  limit=${X}

Should be ${X} collection results
    # Wait until element is visible  css=#content-core
    # below should work for both collections and contentlisting tiles
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//span[@class='summary']  limit=${X}

Should be ${X} pages
    ${X}=  evaluate  ${X} + 1  # need we have next or previous
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//nav[@class='pagination']//a  limit=${X}

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
    Click element  xpath=//nav[@class='pagination']//a[${page}]

Ajax has completed
    Wait For Condition	return jQuery.active == 0  timeout=5 sec

# --- Setup -------------------------------------------------------------------
I've got a site with a collection
    [arguments]  ${batch}=20
    Log in as site owner
    run keyword if  ${USE_TILES}   run keyword  Enable mosaic layout for page  ${PLONE_URL}/testcollection  batch=${batch}
    run keyword unless  ${USE_TILES}   Go to  ${PLONE_URL}/testcollection
    run keyword unless  ${USE_TILES}   Set Batch Size  ${batch}


My collection has a collection search
    run keyword if  ${USE_TILES}  My collection has a collection search tile 
    run keyword unless  ${USE_TILES}  My collection has a collection search portlet

My collection has a collection filter
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns  @{options}
    run keyword if  ${USE_TILES}  My collection has a collection filter tile  ${group_by}  ${op}  ${style}  @{options}
    run keyword unless  ${USE_TILES}  My collection has a collection filter portlet  ${group_by}  ${op}  ${style}  @{options}

My collection has a collection sorting
    [Arguments]  ${sort_on}=sortable_title
    run keyword if  ${USE_TILES}  My collection has a collection sorting tile  ${sort_on}
    run keyword unless  ${USE_TILES}  My collection has a collection sorting portlet  ${sort_on}

My collection has a collection info
    [Arguments]  ${header}="Current Filter"  @{templates}  ${hide_when}=${None}
    run keyword if  ${USE_TILES}  My collection has a collection info tile  ${header}   @{templates}  hide_when=${hide_when} 
    run keyword unless  ${USE_TILES}  My collection has a collection info portlet  ${header}   @{templates}  hide_when=${hide_when} 

I'm viewing the collection
    run keyword if  ${USE_TILES}  Go to  ${PLONE_URL}/testcollection
    run keyword unless  ${USE_TILES}  Go to  ${PLONE_URL}/testcollection
    # Should be 3 collection results


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
    [Arguments]  ${sort_on}=sortable_title

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add sorting portlet  ${sort_on}  links

My collection has a collection info portlet
    [Arguments]  ${header}="Current Filter"  @{templates}  ${hide_when}=${None}

    Go to  ${PLONE_URL}/testcollection
    Manage portlets
    Add info portlet  ${header}   @{templates}  hide_when=${hide_when}  

Open collection settings
    
movable removable mosaic-tile 


Set Batch Size
    [Arguments]   ${batch_size}

    run keyword unless  ${USE_TILES}  Go to  ${PLONE_URL}/testcollection/edit
    run keyword if  ${USE_TILES}  Edit Listing Tile
    Run keyword by label  Item count  Input Text  ${batch_size}
    Click Button  Save
    run keyword if  ${USE_TILES}  Click Button   Save
    # Go to  ${PLONE_URL}/testcollection

Edit Listing Tile
    Go to  ${PLONE_URL}/testcollection/edit
    #Wait until page contains element  css=.mosaic-btn-delete
    #Wait until page contains element   css=#mosaic-panel
    Wait Until Element Is Visible  css=.mosaic-toolbar
    #Unselect Frame
    #mouse over  css=.mosaic-plone.app.standardtiles.contentlisting-tile
    click element  css=.contentlisting-tile
    click button  Edit

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

I should have a filter with ${number_of_results} options
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//aside[contains(@class,'collectionFilter') and count(.//div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')])=${number_of_results} ]  limit=1

I should see ${number} filter options on the page
    Page should contain element  xpath=//aside[contains(@class,'collectionFilter') ]//div[contains(@class, 'filterContent')]//li[contains(@class, 'filterItem')]  limit=${number}


I should not have a portlet titled "${filter_title}"
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and descendant-or-self::*[contains(text(), '${filter_title}')]]

    Page Should not Contain Element  xpath=//${portlet_title_xpath}


I should not see any results
    Wait until keyword succeeds  5s  1s  Element should be visible  xpath=//*[@id="content-core"]/*[text()="No results were found."]

I should have a portlet titled "${filter_title}" with text ${text}
    ${portlet_title_xpath}  Convert to string  header[@class='portletHeader' and contains(text(), '${filter_title}')]
    ${filter_item_xpath}  Convert to string  div[contains(@class, 'portletContent')]

    Page Should Contain Element  xpath=//${portlet_title_xpath}
    Wait Until Element Contains  xpath=//${portlet_title_xpath}/parent::*[contains(@class, 'collectionFilterInfo')]//${filter_item_xpath}  ${text}

I sort by "${sort_on}"
    Wait until element is visible   xpath=//span[contains(normalize-space(text()), '${sort_on}')]
    ${glyph}=  Get Element Attribute  xpath=//span[contains(normalize-space(text()), '${sort_on}')]//span  class
    Click Link  link=${sort on}
    Wait until element is not visible   xpath=//span[contains(normalize-space(text()), '${sort_on}')]//span[@class='${glyph}']

Results Are Sorted
    ${xpath}=    Set Variable    //span[@class='summary']
    ${count}=    Get Element Count    xpath=${xpath}
    ${names}=    Create List
    :FOR    ${i}    IN RANGE    1    ${count} + 1
    \    ${name}=    Get Text    xpath=(${xpath})[${i}]
    \    Append To List    ${names}    ${name}

    ${sorted}=  copy list  ${names}  False
    sort list  ${sorted}
    log many  ${sorted}  ${names}
    run keyword if  $sorted!=$names   Fail   Results are not sorted ${sorted}!=${names}

# --- Tiles -------------------------------------------------------------------


My collection has a collection filter tile
    [Arguments]  ${group_by}=Subject  ${op}=or  ${style}=checkboxes_dropdowns  @{options}

    Go to  ${PLONE_URL}/testcollection/edit
    Add filter tile  ${group_by}  ${op}  ${style}  @{options} 
    Save mosaic page

My collection has a collection search tile

    Go to  ${PLONE_URL}/testcollection/edit
    Add search tile
    Save mosaic page

My collection has a collection info tile
    [Arguments]  ${header}  @{templates}  ${hide_when}=${None}

    Go to  ${PLONE_URL}/testcollection/edit
    Add info tile  @{templates}  hide_when=${hide_when}
    Save mosaic page

My collection has a collection sorting tile 
    [Arguments]  ${sort_on}
    Go to  ${PLONE_URL}/testcollection/edit
    Insert Tile "Result Listing Sort"
    Set Sorting Options  ${sort_on}  links
    Run Keyword by label  Content CSS Selector  Input Text  .contentlisting-tile
    Click element  css=.pattern-modal-buttons #buttons-save
    Drag tile
#    Click button   Edit
    Save mosaic page


Enable mosaic layout for page
    [Arguments]  ${page}  ${batch}=20

    go to  ${page}
    # Setup Mosaic display and open editor
    Click element  link=Display
    Wait Until Element Is visible  css=#plone-contentmenu-display-layout_view
    Click element  link=Mosaic layout
    Go to  ${page}/edit

    wait until element is visible  css=.mosaic-toolbar

    # Create default layout if its a Page
    # Wait Until Element Is Visible  css=.mosaic-select-layout
    # Wait until Page contains element  xpath=//a[@data-value='default/basic.html']
    # Click element  xpath=//a[@data-value='default/basic.html']

    # Enable layout editing
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.mosaic-button-layout
    Wait Until Element Is visible  css=.mosaic-button-customizelayout
    Click element  css=.mosaic-button-customizelayout

    # Add a embed content tile pointing to the collection
    #Add existing content tile  /testcollection
    Add contentlisting tile  ${batch}

    Save mosaic page with bug


Save mosaic page with bug
    Wait Until Element Is Visible  css=.mosaic-button-save   timeout=5 sec
    Click button  css=.mosaic-button-save
    # HACK: Due to bug. If you save it once it works? https://github.com/plone/plone.app.mosaic/issues/421
    Run Keyword And Ignore Error  handle alert
    Wait until page contains  Changes saved   timeout=10 sec


Save mosaic page
    Wait Until Element Is Visible  css=.mosaic-button-save   timeout=5 sec
    Click button  css=.mosaic-button-save
    Wait until page contains  Changes saved   timeout=10 sec


Add filter tile
    [Arguments]   ${group_by}  ${filter_type}  ${input_type}  @{options}

    Insert Tile "Result Filter"
    Drag tile
    Click button   Edit
#    Wait until element is visible  xpath=//div[@class='plone-modal-dialog' and .//*[contains(text(), 'Collection')]]
    #run keyword if  $collection_name  set relateditem  formfield-collective-collectionfilter-tiles-filter-target_collection  ${collection_name}

    Set Filter Options  ${group_by}  ${filter_type}  ${input_type}  @{options}
    Run Keyword by label  Content CSS Selector  Input Text  .contentlisting-tile

    Click element  css=.pattern-modal-buttons #buttons-save


Add search tile
    [Arguments]   ${collection_name}=${None}

    Insert tile "Result Search"
    Drag tile
    Click button  Edit
    run keyword if  $collection_name  set relateditem  formfield-collective-collectionfilter-tiles-search-target_collection  ${collection_name}
    Run Keyword by label  Content CSS Selector  Input Text  .contentlisting-tile
    Click element  css=.pattern-modal-buttons #buttons-save


Add info tile
    [Arguments]   @{templates}  ${hide_when}=${None}  ${collection_name}=${None}

    Insert tile "Result Filter Info"
    run keyword if  $collection_name  set relateditem  formfield-collective-collectionfilter-tiles-info-target_collection  ${collection_name}
    # Complete filter form
    Set Info Settings  collective-collectionfilter-tiles-info  @{templates}  hide_when=${hide_when}
    Run Keyword by label  Content CSS Selector  Input Text  .contentlisting-tile

    Click element  css=.pattern-modal-buttons #buttons-save
    Drag tile

Set Info Settings 
    [Arguments]   ${prefix}  @{templates}  ${hide_when}

    select multi select2 with label  Template Type  @{templates}
    Run keyword if  $hide_when is not ${None}  Run Keyword  select multi select2 with label  Hide when  ${hide_when}



Add existing content tile
    [Arguments]   ${collection_name}=${None}

    Insert tile "Existing Content"
    run keyword if  $collection_name  set relateditem  formfield-plone-app-standardtiles-existingcontent-content_uid    ${collection_name}
    Click element  css=.pattern-modal-buttons #buttons-save

    Drag tile

Add contentlisting tile
    [Arguments]  ${batch}=20
    Insert tile "Content listing"
    Drag tile
    Click button  Edit
    # TODO: test using this method
    # Run Keyword by label  Use query parameters from content  click element

    # Since we aren't using the collection we need to recreate the same settings clickin on select2
    wait until element is visible  link=Select criteria
    select single select2      xpath=(//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-index'])[2]/div  Type
    select multi select2   xpath=(//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-value'])[2]/div  Event  Document

    # TODO: no item count in plone 5.0
    Run Keyword by label  Item count   Input Text  ${batch}

    Click element  css=.pattern-modal-buttons #buttons-save


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

# TODO: doesn't work yet
Set relateditem 
    [Arguments]  ${id}  ${path}
    Wait until element is visible  xpath=//div[@id='${id}']
    Click element  xpath=//div[@id='${id}']//ul[@class='select2-choices']
    Wait until element is visible  xpath=//div[@id='select2-drop']//a[.//text() = '${path}']
    Click element  xpath=//div[@id='select2-drop']//a[.//text() = '${path}']

Insert Tile "${name}"
    Wait Until Element Is Visible  css=.mosaic-toolbar
    Click element  css=.select2-container.mosaic-menu-insert a
    Wait until element is visible  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "${name}"]
    Click element  xpath=//li[contains(@class, "select2-result-selectable") and div/text() = "${name}"]
