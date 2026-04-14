# Report

## Step 1: broad requirements

Process:
- Viewed data. Like Fast5. No timestamps or labels, stored as tensor of ints.
- Broad exploration of aspects of problem

Result:
- Requirements specification version 1 containing broad requirements.

Miscellaneous thoughts:
-  ROIs/bookmarking system useful to create references in the large dataset 
(note: jumping between ROIs might be hard to do in real-time), i.e. we must give users not only the map but
allow them to add landmarks.
- What is more expensive: compute or storage?
- Trade off fast vs accurate: can downsample behind the scenes quickly but does that effect the interpretation of scientists


Next step: refine requirements.
Questions:
- Max amount of data that can be displayed in browser without slowdowns
- Max amount of data that is easy transfer over a network
- What are hosting options

These requirements will inform architecture.

### Goals

Think about:
- Architecture
- Hosting
- Risks
- How to build