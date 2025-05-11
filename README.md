smart_water_management/
├── main.py                    # Starts the app
├── core/
│   ├── prim.py                # Prim’s algorithm logic
│   ├── bfs_simulation.py      # Water flow simulator
│   ├── pressure_monitor.py    # Pressure & leak detection
├── ui/
│   ├── main_window.py         # PyQt6 main window
│   ├── canvas_view.py         # Node drag, edge draw logic
│   ├── sidebar.py             # Buttons: Add, Remove, Simulate, Export
├── visual/
│   └── plotter.py             # matplotlib graph renderer
├── export/
│   └── export_tools.py        # Export to CSV / PNG
├── assets/                    # Icons, logos
├── requirements.txt
└── README.md
