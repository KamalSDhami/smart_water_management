# Smart Water Management System

This is a PyQt6-based desktop application for visualizing and simulating water flow in a network of nodes (houses, sources) and edges (pipes). Features include:
- Add, move, and remove nodes
- Connect and disconnect edges
- Pan and zoom the map
- Toggle a grid overlay
- Simulate water flow and visualize results

## Requirements
- Python 3.8+
- See `requirements.txt` for Python dependencies

## Setup
1. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python main.py
   ```

## Features
- **Node/Edge Editing:** Add, move, remove nodes; connect/disconnect edges
- **Pan/Zoom:** Use the sidebar or mouse to pan/zoom the map
- **Grid:** Toggle a grid overlay for easier alignment
- **Simulation:** Run water flow simulation and view results/graphs

## Notes
- If you encounter missing dependencies, run the included `check_and_install.py` script.
- The UI is scrollable and adapts to different screen sizes.

## License
MIT License 