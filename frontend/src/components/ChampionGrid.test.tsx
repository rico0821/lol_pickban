import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ChampionGrid from './ChampionGrid';

const mockChampions = [
  {
    champion_id: 'Aatrox',
    name: 'Aatrox',
    icon_url: 'https://example.com/Aatrox.png',
  },
  {
    champion_id: 'Ahri',
    name: 'Ahri',
    icon_url: 'https://example.com/Ahri.png',
  },
];

global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ success: true, champions: mockChampions }),
  })
) as jest.Mock;

describe('ChampionGrid', () => {
  it('renders champion grid and displays champions', async () => {
    render(<ChampionGrid />);
    expect(screen.getByText(/Champion Grid/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('Aatrox')).toBeInTheDocument();
      expect(screen.getByText('Ahri')).toBeInTheDocument();
      expect(screen.getAllByRole('img').length).toBe(2);
    });
  });

  it('filters champions by search', async () => {
    render(<ChampionGrid />);
    await waitFor(() => screen.getByText('Aatrox'));
    const input = screen.getByTestId('champion-search');
    fireEvent.change(input, { target: { value: 'ahri' } });
    expect(screen.queryByText('Aatrox')).not.toBeInTheDocument();
    expect(screen.getByText('Ahri')).toBeInTheDocument();
  });

  it('shows empty state if no champions match search', async () => {
    render(<ChampionGrid />);
    await waitFor(() => screen.getByText('Aatrox'));
    const input = screen.getByTestId('champion-search');
    fireEvent.change(input, { target: { value: 'zzz' } });
    expect(screen.getByText('No champions found.')).toBeInTheDocument();
  });
}); 