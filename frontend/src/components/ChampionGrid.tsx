import React, { useEffect, useState } from 'react';

interface Champion {
  champion_id: string;
  name: string;
  icon_url: string;
}

const ChampionGrid: React.FC = () => {
  const [champions, setChampions] = useState<Champion[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/champions')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setChampions(data.champions);
        } else {
          setError('Failed to load champions');
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load champions');
        setLoading(false);
      });
  }, []);

  const filtered = champions.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="w-full">
      <h2 className="text-xl font-bold mb-2">Champion Grid</h2>
      <input
        type="text"
        placeholder="Search champions..."
        className="mb-4 p-2 border rounded w-full"
        value={search}
        onChange={e => setSearch(e.target.value)}
        data-testid="champion-search"
      />
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 max-h-96 overflow-y-auto p-2 border rounded bg-white" data-testid="champion-grid">
        {filtered.map(champ => (
          <div key={champ.champion_id} className="flex flex-col items-center p-2 hover:bg-gray-100 rounded cursor-pointer">
            <img src={champ.icon_url} alt={champ.name} className="w-16 h-16 mb-1 rounded shadow" />
            <span className="text-sm text-center font-medium">{champ.name}</span>
          </div>
        ))}
        {(!loading && filtered.length === 0) && <div className="col-span-full text-center text-gray-500">No champions found.</div>}
      </div>
    </div>
  );
};

export default ChampionGrid; 