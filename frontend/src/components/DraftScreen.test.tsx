import React from 'react';
import { render, screen } from '@testing-library/react';
import DraftScreen from './DraftScreen';

test('renders draft screen with team displays and champion grid', () => {
  render(<DraftScreen />);
  
  // Check for the main title
  expect(screen.getByText(/Draft Screen/i)).toBeInTheDocument();

  // Check for team names
  expect(screen.getByText(/Blue Team/i)).toBeInTheDocument();
  expect(screen.getByText(/Red Team/i)).toBeInTheDocument();

  // Check for the champion grid placeholder
  expect(screen.getByText(/Champion Grid/i)).toBeInTheDocument();
}); 