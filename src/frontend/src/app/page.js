"use client";

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import axios from 'axios';
import styles from './page.module.css';

// Import D3 visualization component
const D3Visualization = dynamic(
  () => import('./components/D3Visualization'),
  { ssr: false }
);

export default function Home() {
  const [data, setData] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [viewport, setViewport] = useState({
    x: 0,
    y: 0,
    zoom: 1
  });
  const [isLoading, setIsLoading] = useState(false);
  const animationRef = useRef(null);
  
  // Set default file and fetch metadata on mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Set the default Zarr file
        await axios.post('http://localhost:8000/set_file', {
          filename: 'mock48_2500hz_1.5h.zarr'
        });
        
        // Fetch metadata
        const response = await axios.get('http://localhost:8000/metadata');
        setMetadata(response.data);
      } catch (error) {
        console.warn('Backend not available - using mock data for development');
      }
    };
    
    initializeApp();
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);
  
  // Fetch initial data when metadata is available
  useEffect(() => {
    if (metadata) {
      fetchData(200, 210);
    }
  }, [metadata]);
  
  // Simulate viewport movement
  // useEffect(() => {
  //   if (!metadata || !data) return;
  //
  //   let time = 0;
  //   const simulateMovement = () => {
  //     // Simulate panning by updating viewport position
  //     time += 0.01;
  //     const newX = Math.sin(time / 1000) * 500;
  //     setViewport(prev => ({
  //       ...prev,
  //       x: newX
  //     }));
  //
  //     // Fetch new data based on viewport position
  //     const startTime = Math.max(0, time);
  //     const endTime = startTime + 10;
  //     fetchData(startTime, endTime);
  //
  //     animationRef.current = requestAnimationFrame(simulateMovement);
  //   };
  //
  //   animationRef.current = requestAnimationFrame(simulateMovement);
  //
  //   return () => {
  //     if (animationRef.current) {
  //       cancelAnimationFrame(animationRef.current);
  //     }
  //   };
  // }, [metadata, data]);
  
  const fetchData = async (startTime, endTime) => {
    if (!metadata || isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/data', {
        start_time: startTime,
        end_time: endTime,
        channel: 1,
        data_type: 'current'
      });
      
      setData(response.data);
    } catch (error) {
      console.warn('Backend not available - generating mock data for development');
      // Generate mock data for development
      const sampleRate = metadata.sample_rate_hz;
      const numSamples = Math.floor((endTime - startTime) * sampleRate);
      const mockData = Array.from({length: numSamples}, (_, i) => 
        Math.sin(i / 100) * Math.random() * 100
      );
      
      setData({
        channel: 0,
        start_time: startTime,
        end_time: endTime,
        sample_rate: sampleRate,
        data: mockData,
        data_type: 'current',
        unit: 'pA'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className={styles.app}>
      <h1>Trace Viewer</h1>
      <div className={styles.info}>
        {metadata && (
          <div>
            <p>Device: {metadata.device_id}</p>
            <p>Channels: {metadata.number_of_channels}</p>
            <p>Sample Rate: {metadata.sample_rate_hz} Hz</p>
            <p>Duration: {metadata.duration_sec} seconds</p>
          </div>
        )}
        {/*{isLoading && <p>Loading data...</p>}*/}
      </div>
      <div className={styles.plotlyContainer}>
        <D3Visualization data={data} viewport={viewport} />
      </div>
    </div>
  );
}