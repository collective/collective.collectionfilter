*** Keywords ***

# Given

a logged-in manager

    Enable autologin as
        ...    Manager

a logged-in test user
    Enable autologin as    Manager
    Create user    my-test-user     Member  Editor  Reviewer  Manager  fullname=John Doe
    Set autologin username    my-test-user


a manage portlets view

    Click  //li[@id="plone-contentmenu-portletmanager"]/a
    Click    //a[@id="portlet-manager-plone.rightcolumn"]
    Get Text    //body    contains    Manage portlets


# When

I add filter portlet
    [Arguments]   ${group_criteria}  ${filter_type}  ${input_type}  @{options}

    Wait For Condition    Element States    //select[contains(@class,"add-portlet")]    contains    visible
    Select Options By    //select[contains(@class,"add-portlet")]    label    Collection Filter
    Wait For Condition    Classes    //body    contains    modal-open
    Type Text  //input[@id="form-widgets-header"]    ${group_criteria}
    Set Filter Options    ${group_criteria}    ${filter_type}    ${input_type}    @{options}
    Click    //div[contains(@class,"modal-footer")]//button[@id="form-buttons-add"]
    Wait For Condition    Element States    //div[contains(@class, 'portletAssignment')]//a[text()='${group_criteria}']    contains    visible

# General

Set Filter Options
    [Arguments]   ${group_by}  ${filter_type}  ${input_type}  @{options}
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


Pause
   Import library    Dialogs
   Pause execution
