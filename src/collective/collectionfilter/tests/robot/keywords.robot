*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    plone/app/robotframework/user.robot

Library    OperatingSystem
Library    Remote    ${PLONE_URL}/RobotRemote
Library    Collections  # needed for "Append To List"

*** Keywords ***

Default Setup
    Run Keyword    Plone Test Setup
    ${USE_TILES}=    Get Environment Variable    ROBOT_USE_TILES    default=${False}
    ${USE_TILES}=    Set Test Variable    ${USE_TILES}
    ${AJAX_ENABLED}=    Get Environment Variable    ROBOT_AJAX_ENABLED    default=${False}
    ${AJAX_ENABLED}=    Set Test Variable    ${AJAX_ENABLED}

Default Teardown
    Run Keyword If Test Failed    Capture Page Screenshot
    Run Keyword If Test Failed    Log Variables
    Run Keyword    Plone Test Teardown

# Given

a logged in test-user
    Enable autologin as    Manager
    Create user    my-test-user     Member  Editor  Reviewer  Contributor    fullname=John Doe
    Set autologin username    my-test-user


a manage portlets view

    Click  //li[@id="plone-contentmenu-portletmanager"]/a
    Click    //a[@id="portlet-manager-plone.rightcolumn"]
    Get Text    //body    contains    Manage portlets


# When

I add filter portlet
    [Arguments]    ${group_criteria}    ${filter_type}    ${input_type}    @{options}

    Wait For Condition    Element States    //select[contains(@class,"add-portlet")]    contains    visible
    Select Options By    //select[contains(@class,"add-portlet")]    label    Collection Filter
    Wait For Condition    Classes    //body    contains    modal-open
    Type Text    //input[@id="form-widgets-header"]    ${group_criteria}
    Set Filter Options    ${group_criteria}    ${filter_type}    ${input_type}    @{options}
    Click    //div[contains(@class,"modal-footer")]//button[@id="form-buttons-add"]
    Wait For Condition    Element States    //div[contains(@class, 'portletAssignment')]//a[text()='${group_criteria}']    contains    visible

# General

Set Filter Options
    [Arguments]    ${group_by}    ${filter_type}    ${input_type}    @{options}
    Select Options By    //select[@id="form-widgets-group_by"]    value    ${group_by}
    Select Options By    //select[@id="form-widgets-filter_type"]    value    ${filter_type}
    Select Options By    //select[@id="form-widgets-input_type"]    value    ${input_type}
    Set Options  @{options}
    Click    //label/span[contains(text(),"Show count")]


Set Options
    [Arguments]  @{options}

    FOR    ${option}    IN    @{options}
        Click    //label[contains(text(),${option})]
    END


Select single select2
    [Arguments]  ${locator}  ${value}
    Click    ${locator}
    Click    //div[contains(@class,'select2-result-label') and text() = '${value}']


Select multi select2
    [Arguments]  ${locator}  @{values}
    FOR  ${value}  IN  @{values}
        # open select2 dropdown
        Click    ${locator}
        # click element
        Click    //div[contains(@class,'select2-result-label') and text() = '${value}']
    END


select multi select2 with label
    [Arguments]  ${label}  @{values}
    # select2 don't have proper labels because the @for doesn't match an id of anything
    ${xpath}=   set variable  //label[normalize-space(text()) ='${label}']/following-sibling::div[contains(@class,'select2-container')]
    Get Element Count    ${xpath}    greater than    0
    Select multi select2    ${xpath}    @{values}


Set sorting Options
    [Arguments]   ${sort_on}  ${input_type}
    select multi select2 with label    Enabled sort indexes    ${sort_on}
    Run Keyword If    ${USE_TILES} == True    Select Options By    //select[@name="collective.collectionfilter.tiles.sortOn.input_type:list"]    value    ${input_type}
    Run Keyword If    ${USE_TILES} == False    Select Options By    //select[@name="form.widgets.input_type:list"]    value    ${input_type}



# Setup

I've got a site with a collection
    [arguments]    ${batch}=20
    a logged in test-user
    Run Keyword If    ${USE_TILES} == True    Enable mosaic layout for page    ${PLONE_URL}/testdoc    batch=${batch}
    Run Keyword If    ${USE_TILES} == False   Go to    ${PLONE_URL}/testcollection
    Run Keyword If    ${USE_TILES} == False   Set Batch Size    ${batch}

Enable mosaic layout for page
    [Arguments]  ${page}=${PLONE_URL}/testdoc  ${batch}=20
    Go To    ${page}

    # Setup Mosaic display and open editor
    Click    //li[@id="plone-contentmenu-display"]/a
    Click    //a[@id="plone-contentmenu-display-layout_view"]
    Go to    ${page}/edit

    # Create default layout if its a Page
    Wait For Condition    Element States  //a[@data-value='default/basic.html']    contains    visible
    Evaluate JavaScript    //body    $("[data-value='default/basic.html']").trigger("click");

    # Enable layout editing
    Click    css=.mosaic-button-customizelayout

    # Add a embed content tile pointing to the collection
    # Add existing content tile  /testdoc
    Run Keyword If    ${batch}>0    Add Contentlisting Tile    ${batch}

    Save mosaic page



Set Batch Size
    [Arguments]   ${batch_size}

    Run Keyword If    ${USE_TILES} == False    Go to  ${PLONE_URL}/testcollection/edit
    Run Keyword If    ${USE_TILES} == True    Edit Listing Tile
    Type Text    //input[@id="form-widgets-ICollection-item_count"]    ${batch_size}
    Run Keyword if    ${USE_TILES} == True    Click  css=.pattern-modal-buttons #buttons-save
    Click    css=#form-buttons-save

My collection has a collection filter
    [Arguments]    ${group_by}=Subject    ${op}=or    ${style}=checkboxes_dropdowns    @{options}
    run keyword if    ${USE_TILES}    My collection has a collection filter tile    ${group_by}    ${op}    ${style}    @{options}
    run keyword if    ${USE_TILES}==False    My collection has a collection filter portlet    ${group_by}    ${op}    ${style}    @{options}


My collection has a collection sorting
    [Arguments]  ${sort_on}=Sortable Title
    Run Keyword If    ${USE_TILES} == True    My collection has a collection sorting tile    ${sort_on}
    Run Keyword If    ${USE_TILES} == False    My collection has a collection sorting portlet    ${sort_on}


My collection has a collection sorting tile
    [Arguments]  ${sort_on}=Sortable Title
    Open advanced mosaic editor
    Insert Tile    "Collection Result Listing Sort"
    Set Sorting Options    ${sort_on}    links
    Click    css=.pattern-modal-buttons #buttons-save
    Drag tile
    Save mosaic page


My collection has a collection sorting portlet
    [Arguments]  ${sort_on}=Sortable Title

    Go to  ${PLONE_URL}/testcollection
    a manage portlets view
    Add sorting portlet    ${sort_on}    links

My collection has a collection filter portlet
    [Arguments]    ${group_by}=Subject    ${op}=or    ${style}=checkboxes_dropdowns    @{options}

    Go to    ${PLONE_URL}/testcollection
    a manage portlets view
    I add filter portlet    ${group_by}    ${op}    ${style}    @{options}


Add sorting portlet
    [Arguments]   ${sort_on}  ${input_type}

    Select Options By    css=select.add-portlet    text    Collection Filter Result Sorting
    Type Text    css=input#form-widgets-header    Sort on
    Set Sorting Options    ${sort_on}    ${input_type}
    Click    css=.modal-footer button#form-buttons-add
    Get Element Count    //div[contains(@class, 'portletAssignment')]//a[text()='Sort on']    greater than    0


I'm viewing the collection
    Run Keyword If    ${USE_TILES} == True    Go to  ${PLONE_URL}/testdoc
    Run Keyword If    ${USE_TILES} == False    Go to  ${PLONE_URL}/testcollection
    # should be 6 items in result


Page should not contain
    [Arguments]   ${text}
    Get Text    //body    not contains    ${text}

# Mosaic

Add Contentlisting Tile
    [Arguments]    ${batch}=20

    Insert Tile    "Content listing"
    Drag tile
    Edit Current Tile

    # set path criteria depth to unlimited
    #Select from list by value  css=select.querystring-criteria-depth  -1

    # Since we aren't using the collection we need to recreate the same settings clickin on select2
    Wait For Condition    Element States    //a/span[contains(text(),"Select criteria")]    contains    visible
    Select single select2  (//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-index'])[2]/div    Type
    Select multi select2  (//div[@id='formfield-plone-app-standardtiles-contentlisting-query']//div[@class='querystring-criteria-value'])[2]/div    Event    Page
    Type Text    //input[@id="plone-app-standardtiles-contentlisting-item_count"]    ${batch}
    Capture Page Screenshot
    Click    css=.pattern-modal-buttons #buttons-save

Insert Tile
    [Arguments]    ${name}="A Tile"
    Click  css=.mosaic-toolbar .select2-container.mosaic-menu-insert a
    Click  //li[contains(@class, "select2-result-selectable") and div/text() = ${name}]

Edit Current Tile
    Click    css=.mosaic-selected-tile .mosaic-btn-settings

Drag Tile
    Wait For Condition    Element States  css=.mosaic-helper-tile-new    contains    visible
    Set Style    css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom    display    block
    Wait For Condition    Element States  css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom    contains    visible
    Mouse Move Relative To    css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom    1    1
    Click    css=.mosaic-IDublinCore-description-tile .mosaic-divider-bottom

Save mosaic page
    Click    css=.mosaic-button-save
    Get Text    //body    contains    Changes saved


# Tiles

Open advanced mosaic editor
    Go to  ${PLONE_URL}/testdoc/edit
    Wait For Condition    Element States  //div[@id="content" and contains(@class,"mosaic-panel")]    contains    visible
    Evaluate JavaScript    //body    $("#content.mosaic-panel").addClass("mosaic-advanced")
    Wait For Condition    Element States    css=.mosaic-advanced    contains    visible
    # d-index fix until fixed in mosaic
    Set Style    css=.mosaic-IDublinCore-description-tile    zIndex    unset


Pause
   Import library    Dialogs
   Pause execution

Set Style
    [Arguments]    ${selector}    ${style}    ${value}
    Evaluate JavaScript    ${selector}    element => element.style.setProperty("${style}", "${value}")


# Core Functions

I sort by "${sort_on}"
    Wait For Condition    Element States    //span[contains(normalize-space(text()), '${sort_on}')]    contains    visible
    ${glyph}=  Get Attribute    //span[contains(normalize-space(text()), '${sort_on}')]//span    class
    Click    //a/span[contains(text(), "${sort on}")]
    Wait For Condition    Element States    //span[contains(normalize-space(text()), '${sort_on}')]//span[@class='${glyph}']    contains    hidden


Results Are Sorted
    ${xpath}=    Set Variable if  ${USE_TILES} == True    //span[@class='summary']    //div[@class='entries']//a[contains(@class, 'url')]
    ${count}=    Get Element Count    ${xpath}
    ${names}=    Create List
    FOR    ${i}    IN RANGE    1    ${count} + 1
        ${name}=    Get Text    (${xpath})[${i}]
        Append To List    ${names}    ${i}${name}
    END

    ${sorted}=    copy list    ${names}    False
    sort list    ${sorted}
    log many    ${sorted}  ${names}
    Run Keyword If    ${sorted}!=${names}    Fail    Results are not sorted ${sorted}!=${names}

# CF Stuff
Should be ${X} collection results
    ${xpath}=  Set Variable if    ${USE_TILES}    //span[@class='summary']    //div[@class='entries']/article
    Run keyword if  ${X}>0    Wait For Condition    Element Count    xpath=${xpath}    >=    ${X}
    # we need a short pause for rendering the collection result
    Sleep  0.5
    ${count} =  Get Element Count    xpath=${xpath}
    Should Be Equal as Numbers    ${count}    ${X}


Should be ${X} pages
    ${X}=  evaluate    ${X} + 1  # need we have next or previous
    Get Element Count    xpath=//ul[@class='pagination']//a    ==    ${X}


Should be filter checkboxes
    [Arguments]    @{values}
    Labels Should Equal  xpath=//div[contains(@class, 'filterContent')]//span[@class='filterLabel']    @{values}

Click Page "${page}"
    Click    xpath=(//ul[@class='pagination']//a)[${page}]

Labels Should Equal
    [Arguments]    ${selector}    @{expect}
    @{locators}=  Get Elements    ${selector}
    ${result}=  Create List
    FOR    ${locator}    IN    @{locators}
           ${name}=    Get Text    ${locator}
           Append To List    ${result}    ${name}
    END

    # USE_TILES differs from order
    sort list    ${expect}
    sort list    ${result}

    Should Be Equal    ${expect}    ${result}

# Misc

Click Input "${label}"
    Click    xpath=//input[@id=//label[.//*[normalize-space(text())='${label}'] or normalize-space(text()) ='${label}']/@for]
