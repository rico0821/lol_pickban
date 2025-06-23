import React from 'react';

interface TeamDisplayProps {
  teamName: string;
}

const TeamDisplay: React.FC<TeamDisplayProps> = ({ teamName }) => {
  return (
    <div>
      <h3>{teamName}</h3>
      {/* Bans and picks will go here */}
    </div>
  );
};

export default TeamDisplay; 