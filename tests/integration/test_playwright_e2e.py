import pytest
from playwright.sync_api import Page, expect

FRONTEND_URL = "http://localhost:3001"

@pytest.mark.playwright
def test_champion_grid_renders(page: Page):
    """E2E: Ensure the champion grid renders at least one champion name."""
    page.goto(FRONTEND_URL, wait_until="networkidle")
    # Wait for the champion grid to appear
    grid = page.locator('[data-testid="champion-grid"]')
    grid.wait_for(state="visible", timeout=10000)
    # Find all champion name spans inside the grid
    names = grid.locator('span')
    count = names.count()
    found = False
    for i in range(count):
        if names.nth(i).inner_text().strip():
            found = True
            break
    if not found:
        page.screenshot(path="../logs/playwright_champion_grid_fail.png")
    # Print debug logs from the hidden debug div
    debug_log = page.locator('[data-testid="champion-debug"]').inner_text()
    print("\n[ChampionGrid Debug Logs from DOM]\n" + (debug_log or "<no logs>"))
    assert count > 0, "No champion names rendered in the grid."
    assert found, "No champion names with text found in the grid." 