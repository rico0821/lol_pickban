import React from 'react';

interface TeamDisplayProps {
  teamName: string;
}

const TeamDisplay: React.FC<TeamDisplayProps> = ({ teamName }) => {
  return (
    <div>
      <h3>{teamName}</h3>
    </div>
  );
};

export default TeamDisplay; 