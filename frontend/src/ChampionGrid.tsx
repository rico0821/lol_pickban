import React, { useEffect, useState, useRef } from 'react';

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
  const debugLogRef = useRef<string[]>([]);

  function logDebug(msg: string) {
    debugLogRef.current.push(msg);
  }

  useEffect(() => {
    const url = '/api/champions';
    logDebug('Fetching ' + url + ' from window.location=' + window.location.href);
    fetch(url)
      .then(async res => {
        logDebug('Received response from ' + url);
        const text = await res.text();
        logDebug('Raw response text: ' + text.slice(0, 500));
        let data;
        try {
          data = JSON.parse(text);
        } catch (e) {
          logDebug('JSON parse error: ' + e);
          setError('Failed to load champions');
          setLoading(false);
          return;
        }
        logDebug('Parsed JSON: ' + JSON.stringify(data));
        if (data.success) {
          setChampions(data.champions);
        } else {
          setError('Failed to load champions');
        }
        setLoading(false);
      })
      .catch(e => {
        logDebug('Fetch error: ' + e);
        setError('Failed to load champions');
        setLoading(false);
      });
    // eslint-disable-next-line
  }, []);

  const filtered = champions.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="w-full max-w-4xl">
      <input
        type="text"
        className="mb-4 p-2 border rounded w-full"
        placeholder="Search champions..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        data-testid="champion-search"
      />
      {loading ? (
        <div className="text-center">Loading...</div>
      ) : error ? (
        <div className="text-red-500 text-center">{error}</div>
      ) : (
        <div
          className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4 max-h-[60vh] overflow-y-auto p-2 bg-white rounded shadow"
          data-testid="champion-grid"
        >
          {filtered.length === 0 ? (
            <div className="col-span-full text-center">No champions found.</div>
          ) : (
            filtered.map(champ => (
              <div
                key={champ.champion_id}
                className="flex flex-col items-center p-2 hover:bg-gray-100 rounded cursor-pointer"
              >
                <img
                  src={champ.icon_url}
                  alt={champ.name}
                  className="w-16 h-16 object-contain mb-2 border border-gray-200 rounded"
                  loading="lazy"
                />
                <span className="text-xs text-center font-medium">{champ.name}</span>
              </div>
            ))
          )}
        </div>
      )}
      {/* Hidden debug log for E2E */}
      <div data-testid="champion-debug" style={{ display: 'none' }}>
        {debugLogRef.current.join('\n')}
      </div>
    </div>
  );
};

export default ChampionGrid; 