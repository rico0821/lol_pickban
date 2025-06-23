import React from 'react';
import { render, screen } from '@testing-library/react';
import ChampionGrid from './ChampionGrid';

test('renders champion grid placeholder', () => {
  render(<ChampionGrid />);
  expect(screen.getByText(/Champion Grid/i)).toBeInTheDocument();
}); 