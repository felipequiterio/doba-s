from streamlit_elements import elements, dashboard
from app.components.input_card import render_input_card


def init_dashboard():
    with elements("dashboard"):
        # Define the layout for all dashboard items
        layout = [
            dashboard.Item("input_card", 0, 0, 4, 4),
            # Add more items here as needed
        ]

        # Initialize the dashboard grid
        with dashboard.Grid(
            layout,
            sx={
                "minHeight": "100vh",
                "width": "100%",
                "background": "#1A1C1E",
            },
            # draggableHandle=".dragHandle",
            # cols=6,
            # rows=12,
            rowHeight=60,
            gap=20,
        ):
            # Render dashboard components
            render_input_card()
            # Add more component renders here
