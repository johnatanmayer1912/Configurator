# QA Checklist for Code Changes

This checklist must be followed after every code change to ensure quality and prevent regressions.

## Pre-Change Validation
- [ ] **Understand the requirement**: Clearly understand what the change is supposed to accomplish
- [ ] **Identify affected areas**: List all files, functions, and components that will be impacted
- [ ] **Backup current state**: Ensure version control is clean before making changes
- [ ] **Review existing tests**: Check if there are existing tests for the affected code

## Code Change Validation
- [ ] **Follow coding standards**: Adhere to project's style guide and conventions
- [ ] **Maintain consistency**: Ensure changes match the existing aesthetic and architectural patterns
- [ ] **No hardcoded values**: Use configuration variables or constants instead of magic numbers/strings
- [ ] **Error handling**: Add appropriate try-catch blocks and error messages
- [ ] **Input validation**: Validate all user inputs and handle edge cases
- [ ] **Accessibility**: Ensure changes don't break accessibility (ARIA labels, keyboard navigation, screen readers)

## Wizard Navigation Testing (Critical)
- [ ] **Forward navigation**: Test moving forward through all 8 wizard steps
- [ ] **Backward navigation**: Test moving backward through all wizard steps
- [ ] **State persistence**: Verify that user input is saved when navigating away from a step
- [ ] **State restoration**: Verify that user input is restored when returning to a step
- [ ] **Step skipping**: Test jumping to specific steps using step buttons
- [ ] **Mode switching**: Test switching between Quick and Architect wizard modes
- [ ] **Scenario selection**: Test expert scenario selection and state preservation

## UI/UX Testing
- [ ] **Visual consistency**: Check that new elements match the design system (spacing, colors, typography, border-radius)
- [ ] **Responsive design**: Test at breakpoints: 1440px, 1024px, 768px, 480px
- [ ] **Hover states**: Verify all interactive elements have proper hover states
- [ ] **Focus states**: Verify keyboard navigation shows clear focus indicators
- [ ] **Loading states**: Ensure loading indicators appear during async operations
- [ ] **Error states**: Verify error messages are clear and actionable
- [ ] **Empty states**: Check that empty lists/panels show appropriate empty state UI

## Functional Testing
- [ ] **Form inputs**: Test all form fields (text, select, checkbox, textarea)
- [ ] **Buttons**: Test all button clicks and their expected actions
- [ ] **Modals**: Test modal open/close functionality and backdrop behavior
- [ ] **Dynamic content**: Test that dynamically added/removed elements work correctly
- [ ] **Data persistence**: Verify data is saved to the correct location
- [ ] **File operations**: Test file generation, saving, and export functionality

## Integration Testing
- [ ] **API calls**: Test all API endpoints that the change affects
- [ ] **Data flow**: Verify data flows correctly between components
- [ ] **State management**: Test that global state updates correctly
- [ ] **Event handling**: Test that events trigger the correct handlers
- [ ] **Third-party libraries**: Verify integration with external libraries still works

## Regression Testing
- [ ] **Previous fixes**: Re-test issues that were fixed in previous changes
- [ ] **Known issues**: Check that known issues haven't reappeared
- [ ] **Related features**: Test features that are related to the change
- [ ] **Edge cases**: Test boundary conditions and unusual inputs

## Performance Testing
- [ ] **Load time**: Verify the application loads without significant delay
- [ ] **Memory usage**: Check for memory leaks or excessive memory consumption
- [ ] **Render performance**: Ensure UI updates are smooth (60fps for animations)
- [ ] **Large datasets**: Test with large amounts of data (many VLANs, interfaces, etc.)

## Security Testing
- [ ] **Input sanitization**: Ensure all user inputs are sanitized
- [ ] **XSS prevention**: Verify no cross-site scripting vulnerabilities
- [ ] **Sensitive data**: Ensure passwords and sensitive data are handled securely
- [ ] **File access**: Verify file operations don't expose sensitive paths

## Browser Compatibility
- [ ] **Chrome**: Test in latest Chrome
- [ ] **Firefox**: Test in latest Firefox
- [ ] **Edge**: Test in latest Edge
- [ ] **Safari**: Test in latest Safari (if applicable)

## Accessibility Testing
- [ ] **Keyboard navigation**: Test full application using only keyboard (Tab, Enter, Space, Arrow keys)
- [ ] **Screen reader**: Test with NVDA or JAWS screen reader
- [ ] **Color contrast**: Verify text meets WCAG AA contrast ratios
- [ ] **ARIA attributes**: Ensure all interactive elements have proper ARIA labels
- [ ] **Focus management**: Verify focus moves logically through the interface

## Documentation Updates
- [ ] **Code comments**: Update or add comments for complex logic
- [ ] **README**: Update README if the change affects user-facing features
- [ ] **CHANGELOG**: Add entry to changelog describing the change
- [ ] **API docs**: Update API documentation if applicable

## Test Coverage
- [ ] **Unit tests**: Add unit tests for new functions
- [ ] **Integration tests**: Add integration tests for new workflows
- [ ] **E2E tests**: Add end-to-end tests for critical user paths
- [ ] **Test existing**: Run all existing tests to ensure no regressions

## Deployment Readiness
- [ ] **Version update**: Update version number in VERSION file
- [ ] **Spec file**: Update PyInstaller spec file with new version
- [ ] **Build script**: Update build script with new version references
- [ ] **Build test**: Build the executable and verify it works
- [ ] **Installation test**: Test the executable on a clean system

## Post-Deployment Monitoring
- [ ] **Error logs**: Check for any errors in the application logs
- [ ] **User feedback**: Monitor for user-reported issues
- [ ] **Performance**: Monitor application performance metrics
- [ ] **Rollback plan**: Have a rollback plan ready if issues are discovered

## Issue-Specific Checks (Update as issues are found)
- [ ] **Wizard state persistence**: After any wizard navigation code change, test forward/back navigation through all steps
- [ ] **CSS design system**: After any CSS change, verify spacing, typography, colors, and border-radius consistency
- [ ] **Form validation**: After any form code change, test validation logic and error messages
- [ ] **File operations**: After any file-related change, test file generation and export

## Sign-off
- [ ] **Self-review**: Review your own changes against this checklist
- [ ] **Peer review**: Have another developer review the changes (if applicable)
- [ ] **QA approval**: Get approval from QA team (if applicable)
- [ ] **Documentation**: Ensure all documentation is updated
- [ ] **Tests passing**: Verify all tests pass
- [ ] **Ready to deploy**: Confirm readiness for deployment

---

## Last Updated: 2026-07-07
## Version: 1.0
