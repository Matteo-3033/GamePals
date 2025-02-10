# Video Games Copilot Architecture

This repository provides an implementation of a **Video Games Copilot Architecture**, where a **Pilot** and a **Copilot** share control over a game instance. The Pilot defines how they want assistance from the Copilot, which can be either a **secondary player** or a **software agent**.

## Project Structure

The project is organized into the following directories:

- **agents/** – Contains the Pilot, Copilot, and any necessary observers.

- **command\_arbitrator/** – Manages command arbitration between the Pilot and the Copilot.

- **doom/** – Implements a rule-based software agent specifically for Doom.

- **game\_controllers/** – Handles both virtual and physical game controller inputs and outputs.

This architecture aims to enhance accessibility and gameplay experiences by allowing flexible shared control between humans and AI or other players.

The following schematic illustrates the interaction between the components of the Architecture:

![Copilot Architecture](assets/architecture.png)