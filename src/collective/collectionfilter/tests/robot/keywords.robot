
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

Select related filter collection
    Click element  css=div.pattern-relateditems-container input.select2-input
    Wait until page contains element  xpath://ul[@class='select2-results']//a[@data-path='/']
    Click link  xpath://ul[@class='select2-results']//a[@data-path='/']
    Wait until page contains element  xpath://ul[@class='select2-results']//a[@data-path='/testcollection']
    Click link  xpath://ul[@class='select2-results']//a[@data-path='/testcollection']

Add search portlet
    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Search
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  Searchable Text
    Select related filter collection
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath://div[@class='portletAssignments']//a[text()='Searchable Text']

Add filter portlet
    [Arguments]   ${group_criteria}  ${filter_type}  ${input_type}

    Wait until page contains element  css=select.add-portlet
    Select From List by label  css=select.add-portlet  Collection Filter
    Wait until element is visible  css=input#form-widgets-header

    Input text  css=input#form-widgets-header  ${group_criteria}
    Select related filter collection
    Select from List by value  css=select#form-widgets-group_by  ${group_criteria}
    Click element  css=input#form-widgets-show_count-0
    Select from List by value  css=select#form-widgets-filter_type  ${filter_type}
    Select from List by value  css=select#form-widgets-input_type  ${input_type}
    Click element  css=.plone-modal-footer input#form-buttons-add
    Wait until page contains element  xpath://div[contains(@class, 'portletAssignments')]//a[text()='${group_criteria}']
