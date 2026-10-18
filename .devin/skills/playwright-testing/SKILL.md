# Playwright Testing Skill

## Description
Expert Playwright testing specialist for end-to-end browser automation, UI interaction testing, and visual regression testing. Masters Playwright's API for reliable, flake-free tests with proper selectors, waiting strategies, and error handling.

## When to Use
- Creating or fixing Playwright E2E tests
- Debugging UI interaction failures (click, fill, select)
- Handling timing issues and element visibility
- Modal/dialog interaction testing
- Form validation testing through UI
- Multi-step wizard flows

## Key Principles

### 1. Proper Selectors
- Use data-testid attributes when possible
- Prefer text-based selectors over CSS selectors
- Use role-based selectors (getByRole)
- Avoid brittle CSS selectors that depend on DOM structure

### 2. Waiting Strategies
- Always wait for elements to be visible/attached before interaction
- Use waitForSelector with explicit timeout
- Use waitForResponse for API calls
- Never use sleep() as primary waiting mechanism

### 3. Modal/Dialog Handling
- Wait for modal to be visible before interaction
- Check for overlay/backdrop elements
- Handle modal close animations
- Verify modal is fully hidden after closing

### 4. Form Interaction
- Clear inputs before filling
- Use fill() for text inputs
- Use selectOption() for dropdowns
- Use check()/uncheck() for checkboxes
- Verify form state after interaction

### 5. Error Handling
- Use try-catch for expected failures
- Log detailed error context
- Take screenshots on failure
- Provide clear error messages

## Common Patterns

### Click Element with Wait
```python
await page.wait_for_selector('[data-testid="button"]', state="visible")
await page.click('[data-testid="button"]')
```

### Fill Form
```python
await page.fill('[name="username"]', "testuser")
await page.fill('[name="password"]', "password")
await page.click('[type="submit"]')
```

### Select Dropdown
```python
await page.select_option('[name="role"]', "admin")
```

### Handle Modal
```python
# Open modal
await page.click('[data-action="open-modal"]')
await page.wait_for_selector('.modal', state="visible")

# Interact with modal
await page.fill('.modal input[name="field"]', "value")
await page.click('.modal button[type="submit"]')

# Wait for modal to close
await page.wait_for_selector('.modal', state="hidden", timeout=5000)
```

### Wait for API Response
```python
with page.expect_response("**/api/endpoint") as response_info:
    await page.click('[data-action="submit"]')
response = response_info.value
assert response.status == 200
```

## Debugging Tips

1. **Take Screenshots**: `await page.screenshot(path="debug.png")`
2. **Inspect State**: `print(await page.inner_html("body"))`
3. **Slow Motion**: Use `slow_mo=1000` in browser launch for debugging
4. **Headed Mode**: Use `headless=False` to see the browser
5. **Trace Viewer**: Use `--tracing` to capture execution traces

## Anti-Patterns to Avoid

- Never use `time.sleep()` as primary waiting mechanism
- Never use CSS selectors that depend on DOM structure depth
- Never assume elements are immediately available
- Never ignore timeout errors without investigation
- Never use brittle XPath selectors

## File Structure

Tests should be organized by feature:
```
tests/e2e/
├── test_auth.py
├── test_wizard.py
├── test_templates.py
└── test_validation.py
```

## Best Practices

1. Each test should be independent and runnable alone
2. Use fixtures for common setup (page, login, etc.)
3. Clean up after tests (close modals, reset state)
4. Use descriptive test names
5. Add comments for complex interactions
6. Group related tests in classes
