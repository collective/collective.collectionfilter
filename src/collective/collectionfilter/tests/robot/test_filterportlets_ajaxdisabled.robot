
*** Settings *****************************************************************

Resource  keywords.robot

# Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: Searching through a portlet with ajax disabled
    Given I've got a site with a collection
      and my collection has a collection search portlet
      and my collection has a collection filter portlet
      and I'm viewing the collection
    When I search for "Document" and click search
    Then should be 1 collection results
      and should be 3 filter options

    # Searching for query keywords (https://github.com/collective/collective.collectionfilter/issues/85)
    When I search for "and Document" and click search
    Then I should not see any results
      and I should have a portlet titled "Subject" with 0 filter options
    When I search for "or Document" and click search
    Then I should not see any results
      and I should have a portlet titled "Subject" with 0 filter options
    When I search for "not Document" and click search
    Then I should not see any results
      and I should have a portlet titled "Subject" with 0 filter options

    # the following doesn't work ... I think no 'keyup' event is fired
    # Given I'm viewing the collection
    # When I search for ${EMPTY} and click search
    # Then should be 2 collection results
    #   and should be 4 filter options