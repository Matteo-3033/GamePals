# Video Games Copilot Architecture

This repository provides the building blocks of a **Video Games Copilot Architecture**, where multiple **Input Sources** share control over a game instance.  
Two Architecture implementations are provided:
- A **Pilot-Copilot Architecture**, where a **primary player** Pilot defines how they want assistance from a Copilot, which can be either a **secondary player** or a **software agent**.
- A **Multiple-Sources Architecture**, where inputs from a deliberate number of Input Sources are combined into a single Source.

## Project Structure

The project is organized into the following directories:

- **agents/** – Contains the Input Source class, the Pilot and an abstract class for a Copilot implementation.

  - **agents/observers** - Contains the Observer classes, to listen to generic Inputs, Pilot Inputs or Copilot Inputs.

- **command\_arbitrators/** – Manages command arbitration between Input Sources. In particular, a Pilot-Copilot Arbitrator and a Multi-Source Arbitrator are provided.

- **doom/** – Implements a rule-based software agent specifically for Doom.

  - **doom/copilots** - Implements the action-specific Copilots for Doom.

  - **doom/observers** - Contains the Observer Classes for the Doom package.

- **game\_controllers/** – Handles both virtual and physical game controller inputs and outputs.

This architecture aims to enhance accessibility and gameplay experiences by allowing flexible shared control between humans and Software Agents or other players.

The following schematic illustrates the interaction between the components of the Architecture:

![Copilot Architecture](assets/architecture.png)