import React from 'react';
import { render, screen } from '@testing-library/react';
import ChampionGrid from './ChampionGrid';

test('renders champion grid skeleton', () => {
  render(<ChampionGrid />);
  expect(screen.getByTestId('champion-grid')).toBeInTheDocument();
  expect(screen.getByText(/Champion Grid/i)).toBeInTheDocument();
}); 