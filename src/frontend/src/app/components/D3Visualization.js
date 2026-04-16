"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import styles from '../page.module.css';

export default function D3Visualization({ data, viewport }) {
  const svgRef = useRef(null);
  
  useEffect(() => {
    if (!data || !data.data || data.data.length === 0 || !svgRef.current) {
      return;
    }

    // Clear previous SVG content
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Set up dimensions
    const width = 800;
    const height = 500;
    const margin = { top: 30, right: 20, bottom: 50, left: 50 };
    
    // Calculate chart dimensions
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    // Create main SVG group with margins
    const mainGroup = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Create a clip path for the zoomable area
    mainGroup.append("defs").append("clipPath")
      .attr("id", "clip")
      .append("rect")
      .attr("width", chartWidth)
      .attr("height", chartHeight);
    
    // Create a group for the zoomable content (data line only)
    const zoomGroup = mainGroup.append("g")
      .attr("clip-path", "url(#clip)");

    // Convert time-series data
    const timeValues = data.data.map((value, index) => index / data.sample_rate);
    const voltageValues = data.data.map(value => value * 100); // Scale for visibility

    // Calculate data domains
    const timeMin = d3.min(timeValues);
    const timeMax = d3.max(timeValues);
    const voltageMin = d3.min(voltageValues);
    const voltageMax = d3.max(voltageValues);

    // Add some padding to the domains
    const timePadding = (timeMax - timeMin) * 0.05; // 5% padding
    const voltagePadding = (voltageMax - voltageMin) * 0.1; // 10% padding

    // Set up scales - initially fit to data domain, then respect viewport
    const xDomain = viewport.x !== 0 || viewport.y !== 0 
      ? [viewport.x, viewport.x + 10] 
      : [timeMin - timePadding, timeMax + timePadding];

    const yDomain = [voltageMin - voltagePadding, voltageMax + voltagePadding];

    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([0, chartWidth])
      .nice();

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([chartHeight, 0])
      .nice();

    // Create line generator
    const line = d3.line()
      .x((d, i) => xScale(timeValues[i]))
      .y(d => yScale(d))
      .curve(d3.curveLinear);

    // Add X axis to main group (not zoomable)
    const xAxisGroup = mainGroup.append("g")
      .attr("transform", `translate(0,${chartHeight})`)
      .call(d3.axisBottom(xScale));
    
    xAxisGroup.append("text")
      .attr("x", chartWidth / 2)
      .attr("y", 40)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .text("Time (s)");

    // Add Y axis to main group (not zoomable)
    const yAxisGroup = mainGroup.append("g")
      .call(d3.axisLeft(yScale));
    
    yAxisGroup.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -chartHeight / 2)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .text("Current (scaled)");

    // Add title (not zoomable)
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("Current Trace");

    // Draw the line in zoom group
    const linePath = zoomGroup.append("path")
      .datum(voltageValues)
      .attr("fill", "none")
      .attr("stroke", "#ff0000")
      .attr("stroke-width", 2)
      .attr("d", line);
    
    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 10]) // Minimum and maximum zoom levels
      .on("zoom", (event) => {
        // Apply zoom transform only to the data (zoom group)
        zoomGroup.attr("transform", event.transform);
        
        // Update axes with the new transformed scales
        const newXScale = event.transform.rescaleX(xScale);
        const newYScale = event.transform.rescaleY(yScale);
        
        xAxisGroup.call(d3.axisBottom(newXScale));
        yAxisGroup.call(d3.axisLeft(newYScale));
      });
    
    // Apply zoom behavior to the main SVG
    mainGroup.call(zoom);

  }, [data, viewport]);

  if (!data || !data.data || data.data.length === 0) {
    return <div className={styles.deckContainer}>No data to display</div>;
  }

  return (
    <div className={styles.deckContainer}>
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }}></svg>
    </div>
  );
}