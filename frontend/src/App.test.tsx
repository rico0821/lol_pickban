import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the main draft screen', () => {
  render(<App />);
  // Check that the main Draft Screen container is rendered, which is the new content of App.
  const draftScreenTitle = screen.getByText(/Draft Screen/i);
  expect(draftScreenTitle).toBeInTheDocument();
});
