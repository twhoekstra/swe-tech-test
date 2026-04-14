# Tool Requirements

---


## 1. Introduction

### 1.1 Purpose

This document outlines the requirements for a browser-based trace viewer designed for scientists
working with electrophysiology recordings from nanopore experiments. 
The primary goal is to provide an intuitive, real-time web browser interface for visualizing 
and navigating large datasets (tens of millions of data points across 48 channels) 
The tool enables users to:

- View single-channel traces and aggregated overviews.
- Mark, name, tag, and navigate Regions of Interest (ROIs).
- Measure voltage/current and event durations.
- Export aggregated metrics and annotated views.
- Identify and analyse events (e.g., blockages, bad channels) across channels (_could-have_ feature).

---

### 1.2 Scope

#### In Scope

- Data Visualization:
  - Rendering of single-channel traces and aggregated overviews (e.g., heatmaps, stacked traces).
  - Dynamic loading and downsampling for smooth pan/zoom operations.
  - Real-time rendering and interactions (except initial load, where a short transition is acceptable) for regardless of user device spec
- User Interaction:
  - The trace viewer is a browser-accessed tool, intended for desktop use.
  - Marking, naming, tagging, and categorizing Regions of Interest (ROIs).
  - Navigation between ROIs via a list view.
  - Measuring voltage/current and event durations.
  - Persisting ROIs in a database for retrieval across sessions.
  - Exporting basic measurement information and visuals to file
- Cloud Hosting:
  - Deployment on a big-3 cloud platform (AWS, GCP, or Azure).
  - Handling of processing like dynamic downsampling, i.e. via serverless functions
  - Auto-scaling for concurrent users.
- Data Management:
  - Storage of raw data in blob storage (e.g., AWS S3, Azure Blob Storage).
  - Metadata and annotations stored in a database (e.g., PostgreSQL).
  - User authentication via company-wide SSO.
  - Accessibility outside the local network (e.g., via VPN or public endpoints with authentication).

#### Out of Scope

- Data Entry: We will not consider how recordings are uploaded to a database.
- Data Editing: Editing or modifying raw data is out of scope.
- File selection: Viewing available files to view and selecting them. 
- Multiple files: Comparing two or more recordings
- Advanced Analysis: No built-in tools for (statistical) analysis
- Collaborative Features: ROIs are user-specific unless explicitly shared (nice-to-have).
- Downstream pipelines: Export/linking of ROIs/events/recordings for downstream processing
- Offline/mobile uses: The tool is not intended for offline use nor  
- Internal use: Seeing as the goal is to view raw recordings (rather than protein fingerprints etc.), we assume
this tool is for internal Portal use. 


---

### 1.3 Definitions, Acronyms, and Abbreviations


| Term          | Definition                                                                                 |
|---------------|--------------------------------------------------------------------------------------------|
| ROI           | Region of Interest: A user-defined segment of a trace marked for annotation or analysis.   |
| Downsampling  | Reducing the resolution of data to optimize performance and storage.                       |
| Latency       | The time delay between a user action (e.g., pan/zoom) and the system’s response.           |
| SSO           | Single Sign-On: Authentication mechanism for company-wide access.                          |
| MoSCoW        | Requirement priortization using labels: must-have, should-have, could-have, and won't-have |


---

## 2. Overall Description

### 2.1 Product

The trace viewer is a browser tool design to facilitate workflow of scientists analysing electrophysiology data. 
It does not replace existing tools but provides a complementary interface for visualization. 
The tool is optimized for large datasets and supports dynamic interactions (pan, zoom) with 
minimal latency. The tool should provide both overviews of the full recording and more in-depth views of the data.

---

### 2.2 User Characteristics

- Technical Proficiency: Users are scientists with varying levels of technical expertise. Minimum expertise level would 
be that employees who are pure experimentalists, who have minimal programming/IT knowledge. 
- Platform: Primarily designed for desktop use. Tablet support is a a _could-have_ feature.
- Assumptions: Users have access to modern computers.

---

### 2.3 Assumptions and Dependencies

- Data Structure: Raw data is stored as 16-bit integers representing current/voltage over time across 48 channels. 
No timestamps or labels are provided. We assumes uniform sampling intervals.
- Cloud Platform: The tool must be deployable on AWS, GCP, or Azure. The final choice will depend on cost, scalability, 
and existing infrastructure.
- Browser Compatibility: The tool must work in Chrome and Firefox without requiring plugins.
- Network Access: The tool must function outside the company’s local network (e.g., via VPN or public endpoints) 
to support working from various locations.

---


## 3. Requirements

### 3.1 Interface requirements

#### 3.1.1 User interfaces

| ID  | Requirement                                        | Priority |
|-----|----------------------------------------------------|----------|
| IR1 | Users shall use the tool through a browser         | High     |
| IR2 | Users shall interact via mouse/trackpad            | High     |
| IR3 | Users shall interact via keyboard shorcuts         | Medium   |
| IR4 | Users must authenticate via company SSO before use | Medium   |
| IR5 | The tool shall have tooltips for first-time users  | Low      |


#### 3.1.2 Software interfaces

| ID  | Requirement                                                                      | Priority |
|-----|----------------------------------------------------------------------------------|----------|
| IR6 | The tool shall require the data files to be uploaded to a specified location[^1] | High     |


[^1]: See scope.

---

### 3.2 Functional Requirements

#### 3.2.1 Data visualization requirements


| ID  | Requirement                                                                                                          | Priority |
|-----|----------------------------------------------------------------------------------------------------------------------|----------|
| FR1 | The tool shall give a users an overview of the full recording                                                        | High     |
| FR2 | The tool shall allow users to select a subset of the data in time or in channels                                     | High     |
| FR3 | The tool shall allow users to view the subset (in time, current/voltage, and channels) in a high-resolution viewport | High     |
| FR4 | Inside the viewport, a user can navigate to adjacent data (i.e. in time) by panning and zooming                      | High     |


#### 3.2.2 User interaction requirements

| ID  | Requirement                                                                                                           | Priority |
|-----|-----------------------------------------------------------------------------------------------------------------------|----------|
| FR1 | A user can select ROIs within the data, are bookmarked                                                                | Medium   |
| FR2 | ROIs should persist between sessions                                                                                  | Medium   |
| FR3 | ROIs are displayed in a list                                                                                          | Medium   |
| FR4 | A user shall be able to navigate between RIOs by clicking on them in a list                                           | Medium   |
| FR5 | Users must be able to mark, name, tag, and categorize ROIs on traces                                                  | Medium   |
| FR6 | Users must be able to mark, name, tag, and categorize ROIs on traces                                                  | Medium   |
| FR7 | Users must be able to measure voltage/current via hover-over tooltips and calculate the duration of selected regions. | Low      |
| FR8 | The UI must include tooltips for first-time users (nice-to-have).                                                     | Low      |
| FR9 | User errors are handled through user-friendly error messages                                                          | High     |


| FR1 | The UI must never show a blank screen during pan/zoom operations. Pre-fetching of data is required.                   | High     |
| FR2 | The tool must support real-time rendering with a latency <100 ms for all interactions (pan, zoom, ROI selection).     | High     |
| FR6 | The tool must support server-side downsampling to optimize data transfer and rendering performance.                   | High     |
| PR3 | Downsampling should be server-side to balance performance and storage.                             | High      |

Two finger pan on laptop mousepad
What is the priority of voltage view

---

### 3.2 Performance Requirements


| ID  | Requirement                                                                                        | Priority  |
|-----|----------------------------------------------------------------------------------------------------|-----------|
| PR1 | Latency for pan/zoom in the viewport must be <100 ms to ensure real-time interaction.              | High      |
| PR2 | The tool must handle large datasets of at least 1GB per recording without performance degradation. | High      |
| PR3 | Performance shall be mostly independent of the hardware avaiable to the user                       | High      |
| PR4 | The system must auto-scale to handle concurrent users.                                             | High      |

---

### 3.3 Design constraints

| ID  | Requirement                                                              | Priority  |
|-----|--------------------------------------------------------------------------|-----------|
| DC1 | The application needs to run on AWS, GCP, or Azure,                      | High      |
| DC2 | Raw data files are stored in blob storage  (AWS S3, Azure Blob Storage). | High      |

---

### 3.4 Software system attributes

| ID  | Requirement                                                                               | Priority |
|-----|-------------------------------------------------------------------------------------------|----------|
| SA1 | Occasional downtime (up to 1/2 day per month) is acceptable.                              | Low      |
| SA2 | Technical errors are logged for administrators                                            | Medium   |
| SA3 | Company-wide SSO is sufficient for authentication                                         | High     |
| SA4 | No GDPR or other compliance requirements, as the tool is for experimental use only        | N/a      |
| SA5 | The tool should be built with a modular architecture to allow for future updates.         | N/a      |
| SA6 | The tools implementation shall leverage the cloud provider’s infrastructure for scaling   | N/a      |

---


## 7. Appendices


### 7.2 References
