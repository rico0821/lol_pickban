import React from 'react';
import { render, screen } from '@testing-library/react';
import TeamDisplay from './TeamDisplay';

test('renders team display with correct team name', () => {
  render(<TeamDisplay teamName="Test Team" />);
  expect(screen.getByText(/Test Team/i)).toBeInTheDocument();
}); 