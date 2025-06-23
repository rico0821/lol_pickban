import React from 'react';
import TeamDisplay from './TeamDisplay';
import ChampionGrid from './ChampionGrid';

const DraftScreen = () => {
  return (
    <div>
      <h1>Draft Screen</h1>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <TeamDisplay teamName="Blue Team" />
        <ChampionGrid />
        <TeamDisplay teamName="Red Team" />
      </div>
    </div>
  );
};

export default DraftScreen; 