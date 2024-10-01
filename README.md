# 🌲 Timber Design

This example function automates the extraction of results and properties from ETABS models to streamline post-processing tasks for structural engineers. It enhances the workflow by performing design checks, allowing engineers to efficiently verify structural elements against design requirements, saving time and reducing manual effort in analysis. 

🚧 _Work in progress!_

## ✨ Features
- Send analysis model with results to a [Speckle project](https://speckle.systems/) using the connectors
- [Automation](https://speckle.systems/features/automation/) triggered based on user inputs
- Elements filtered by material type and desired design process (e.g. design timber columns)
- Design conducted with results returned to Speckle project

## 🚧 Limitations
The project has been written in a way to encourage and allow for ease of extensibility. In its current state, the function provides abstractions for:
- `StructuralModel`:
  - `ETABS`
- `DesignCode`:
  - `Eurocode` - EN 1995-1-1:2004+A1:2008 (E)
- `StructuralElement1D`:
  - Columns
- Material database:
  - Britain

## 📜 Licensing
[Apache-2.0 license](https://github.com/bjoernsteinhagen/timber-design?tab=Apache-2.0-1-ov-file)

## 📚 Docs
[Speckle Automate Docs](https://speckle.guide/automate/)
