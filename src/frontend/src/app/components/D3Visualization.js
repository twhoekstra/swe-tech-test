"use client";

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import styles from "../page.module.css";

export default function D3Visualization({ data, viewport, clipEnabled }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!data || !data.data || data.data.length === 0 || !svgRef.current) {
      return;
    }

    // Get container dimensions
    const container = svgRef.current.parentElement;
    const width = container.clientWidth;
    const height = container.clientHeight;
    const marginTop = 30;
    const marginRight = 20;
    const marginBottom = 50;
    const marginLeft = 50;

    // Clear previous SVG content
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Store path reference for clip updates
    let pathRef = null;

    // Calculate chart dimensions
    const chartWidth = width - marginLeft - marginRight;
    const chartHeight = height - marginTop - marginBottom;


    console.log(data)
    const data_table = data.data.map((y, i) => ({
      x: i,
      y: y * data.scale + data.offset, // Apply scaling to convert to true values
    }));

    // Create the horizontal and vertical scales.
    const x = d3
      .scaleLinear()
      .domain(d3.extent(data_table, (d) => d.x)) // Use the generated X values
      .range([marginLeft, width - marginRight])
      .nice();

    const y = d3
      .scaleLinear()
      .domain(d3.extent(data_table, (d) => d.y)) // Use scaled y values
      .range([height - marginBottom, marginTop])
      .nice();

    // Generator X axis
    const xAxis = (g, x) =>
      g
        .call(
          d3
            .axisBottom(x)
            .ticks(width / 80)
            .tickSizeOuter(0),
        )
        .append("text")
        .attr("x", width / 2)
        .attr("y", 40)
        .attr("fill", "#000")
        .attr("text-anchor", "middle")
        .text("Samples (1)");

    // Generator for Y axis
    const yAxis = (g, y) =>
      g
        .call(
          d3
            .axisLeft(y)
            .ticks(height / 80)
            .tickSizeOuter(0),
        )
        .append("text")
        .attr("y", -height / 2)
        .attr("x", -40)
        .attr("fill", "#000")
        .attr("text-anchor", "middle")
        .text("Current (scaled)");

    // Create line generator, will change later
    const line = (data_table, x, y) => d3.line()
      .curve(d3.curveLinear)
      .x((d) => x(d.x))
      .y((d) => y(d.y))(data_table);

    // Create the zoom behavior.
    const zoom = d3
      .zoom()
      .scaleExtent([1, 32])
      .extent([
        [0, 0],
        [width, height],
      ]) // Full panning area
      .translateExtent([
        [-Infinity, -Infinity],
        [Infinity, Infinity],
      ]) // Unlimited panning in both directions
      .on("zoom", zoomed);

    // Create the SVG container
    svg
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("preserveAspectRatio", "none");

    svg
      .append("clipPath")
      .attr("id", "clip")
      .append("rect")
      .attr("x", marginLeft)
      .attr("y", marginTop)
      .attr("width", chartWidth)
      .attr("height", chartHeight);
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "bold")
      .text("Current Trace");

    const path = svg
      .append("path")
      .attr("clip-path", clipEnabled ? "url(#clip)" : null)
      .attr("fill", "none")
      .attr("stroke", "#ff0000")
      .attr("stroke-width", 2)
      .attr("d", line(data_table, x, y));
    

    // .datum(dataValues)

    const gx = svg
      .append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(xAxis, x);

    const gy = svg
      .append("g")
      .attr("transform", `translate(${marginLeft}, 0)`)
      .call(yAxis, y);

    // Create a group for the zoomable content
    // const zoomGroup = svg.append("g");
    // svg.append("path").attr("class", "line").attr("clip-path", "url(#clip)");

    function zoomed(event) {
      const xz = event.transform.rescaleX(x);
      const yz = event.transform.rescaleY(y);
      path.attr("d", line(data_table, xz, yz));
      gx.call(xAxis, xz);
      gy.call(yAxis, yz);
    }

    // Initial zoom
    svg.call(zoom);
  }, [data, viewport]);

  // Update clip-path when clipEnabled changes
  useEffect(() => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    const path = svg.select("path");
    if (path.node()) {
      path.attr("clip-path", clipEnabled ? "url(#clip)" : null);
    }
  }, [clipEnabled]);



  if (!data || !data.data || data.data.length === 0) {
    return <div className={styles.deckContainer}>No data to display</div>;
  }

  return (
    <div className={styles.deckContainer}>
      <svg ref={svgRef}></svg>
    </div>
  );
}
