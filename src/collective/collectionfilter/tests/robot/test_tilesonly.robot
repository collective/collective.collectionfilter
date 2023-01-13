*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  keywords.robot

Test Setup  Run keyword  Default Setup
Test Teardown  Run keyword  Default Teardown


*** Test Cases ***************************************************************

Scenario: Add filter before content listing
    Given I've got a site without a listing
     When my collection has a collection filter
     then Page should contain  need to add a Content Listing
     When my collection has a collection search
     then Page should contain  need to add a Content Listing
     When my collection has a collection sorting
     then Page should contain  need to add a Content Listing
     When edit mosaic page
      and save mosaic page
     then Page should contain  need to add a Content Listing
     When edit mosaic page
      and Add contentlisting tile
      and save mosaic page
     then Page should not contain  need to add a Content Listing
