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

    // Set up dimensions (matching ObservableHQ example structure)
    const width = 800;
    const height = 500;
    const marginTop = 30;
    const marginRight = 20;
    const marginBottom = 50;
    const marginLeft = 50;

    // Calculate chart dimensions
    const chartWidth = width - marginLeft - marginRight;
    const chartHeight = height - marginTop - marginBottom;

    // Convert time-series data
    const timeValues = data.data.map((value, index) => index / data.sample_rate);
    const voltageValues = data.data.map(value => value * 100); // Scale for visibility

    // Set up scales
    const xScale = d3.scaleLinear()
      .domain([d3.min(timeValues), d3.max(timeValues)])
      .range([marginLeft, width - marginRight])
      .nice();

    const yScale = d3.scaleLinear()
      .domain([d3.min(voltageValues), d3.max(voltageValues)])
      .range([height - marginBottom, marginTop])
      .nice();

    // Create the SVG container
    svg
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height]);

    // Create a clip-path with unique ID
    const clipId = "clip-" + Math.random().toString(36).substr(2, 9);

    svg.append("clipPath")
      .attr("id", clipId)
      .append("rect")
      .attr("x", marginLeft)
      .attr("y", marginTop)
      .attr("width", chartWidth)
      .attr("height", chartHeight);

    // Create line generator
    const line = d3.line()
      .defined(d => !isNaN(d))
      .x((d, i) => xScale(timeValues[i]))
      .y(d => yScale(d))
      .curve(d3.curveLinear);

    // Create X axis
    const xAxis = svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(d3.axisBottom(xScale).ticks(width / 80).tickSizeOuter(0));

    xAxis.append("text")
      .attr("x", width / 2)
      .attr("y", 40)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .text("Time (s)");

    // Create Y axis
    const yAxis = svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(d3.axisLeft(yScale).ticks(null, "s"));

    yAxis.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("x", -height / 2)
      .attr("fill", "#000")
      .attr("text-anchor", "middle")
      .text("Current (scaled)");

    // Add title
    svg.append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("Current Trace");

    // Create a group for the zoomable content
    const zoomGroup = svg.append("g");

    // Move the path into the zoom group
    const path = zoomGroup.append("path")
      .datum(voltageValues)
      .attr("clip-path", `url(#${clipId})`)
      .attr("fill", "none")
      .attr("stroke", "#ff0000")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Create zoom behavior with unlimited panning
    const zoom = d3.zoom()
      .scaleExtent([1, 32])
      .extent([[0, 0], [width, height]])  // Full panning area
      .translateExtent([[-Infinity, -Infinity], [Infinity, Infinity]])  // Unlimited panning in both directions
      .on("zoom", (event) => {
        // Apply transform to the zoom group
        zoomGroup.attr("transform", event.transform);
        
        // Update both axes with the new scales
        const xz = event.transform.rescaleX(xScale);
        const yz = event.transform.rescaleY(yScale);
        
        xAxis.call(d3.axisBottom(xz).ticks(width / 80).tickSizeOuter(0));
        yAxis.call(d3.axisLeft(yz).ticks(height / 40).tickSizeOuter(0));
      });

    // Apply zoom behavior to the SVG
    svg.call(zoom);

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