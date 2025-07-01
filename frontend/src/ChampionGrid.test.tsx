/// <reference types="vitest" />
import { render, screen } from '@testing-library/react';
import ChampionGrid from './ChampionGrid';
import { vi, beforeEach, afterEach, describe, it, expect } from 'vitest';

// Mock fetch for component test
beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(() =>
    Promise.resolve({
      text: () => Promise.resolve(JSON.stringify({ success: true, champions: [] })),
    })
  ));
});
afterEach(() => {
  vi.unstubAllGlobals();
});

describe('ChampionGrid', () => {
  it('renders and shows loading, then empty state', async () => {
    render(<ChampionGrid />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    // Wait for empty state
    const empty = await screen.findByText(/no champions found/i);
    expect(empty).toBeInTheDocument();
  });
}); 