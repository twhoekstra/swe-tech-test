"use client";

import { useRef } from 'react';
import { DeckGL } from '@deck.gl/react';
import { LineLayer } from '@deck.gl/layers';
import styles from '../page.module.css';

export default function DeckVisualization({ data, viewport }) {
  const deckRef = useRef(null);
  
  const renderLayers = () => {
    if (!data || !data.data || data.data.length === 0) {
      return [];
    }
    
    // Convert time-series data to coordinates for LineLayer
    const points = data.data.map((value, index) => [
      index / data.sample_rate, // x = time
      value * 100 // y = voltage (scaled for visibility)
    ]);
    
    return [
      new LineLayer({
        id: 'trace-layer',
        data: [{ path: points }],
        getPath: d => d.path,
        getColor: [255, 0, 0],
        getWidth: 2,
        widthUnits: 'pixels'
      })
    ];
  };
  
  return (
    <div className={styles.deckContainer}>
      <DeckGL
        ref={deckRef}
        initialViewState={
          {
            target: [5, 0],
            zoom: viewport.zoom
          }
        }
        controller={true}
        layers={renderLayers()}
      />
    </div>
  );
}