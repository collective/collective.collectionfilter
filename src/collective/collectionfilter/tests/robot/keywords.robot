
*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot


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
    Element should be visible  css=#plone-contentmenu-portletmanager > ul
    Click element  partial link=Right

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
    Click Input "Show count"
    Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath=//div[contains(@class, 'portletAssignments')]//a[text()='${group_criteria}']


Should be ${X} filter options
    Wait until keyword succeeds  5s  1s  Page Should Contain Element  xpath=//div[contains(@class, 'filterContent')]//*[contains(@class, 'filterItem')]  limit=${X}

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

Set portlet "${title}" "${checkbox}"
    Click Link  ${title}
    Click Input "${checkbox}"
    Click element  css=.plone-modal-footer input#form-buttons-apply
    Wait until page does not contain element  css=.plone-modal-dialog

Click Page "${page}"
    Click element  xpath=//nav[@class='pagination']//a[${page}]
