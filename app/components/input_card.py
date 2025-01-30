from streamlit_elements import mui


def render_input_card():
    with mui.Card(
        key="input_card",
        sx={
            "p": 2,
            "backgroundColor": "#242729",
            "borderRadius": 2,
            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.2)",
            "border": "1px solid rgba(79, 236, 215, 0.1)",
        },
    ):
        with mui.Stack(spacing=2):
            # Chat display area
            mui.Paper(
                sx={
                    "backgroundColor": "#1A1C1E",
                    "borderRadius": "8px",
                    "p": 2,
                    "minHeight": "300px",
                    "maxHeight": "300px",
                    "overflow": "auto",
                    "color": "#FFFFFF",
                    "fontFamily": "system-ui",
                    "border": "1px solid rgba(79, 236, 215, 0.1)",
                }
            )

            # Input area
            with mui.Stack(direction="row", spacing=2, alignItems="center"):
                mui.TextField(
                    placeholder="Type your message...",
                    size="small",
                    fullWidth=True,
                    sx={
                        "flex": 1,
                        "& .MuiOutlinedInput-root": {
                            "backgroundColor": "#1A1C1E",
                            "borderRadius": "8px",
                            "& fieldset": {
                                "borderColor": "rgba(79, 236, 215, 0.2)",
                            },
                            "&:hover fieldset": {
                                "borderColor": "rgba(79, 236, 215, 0.4)",
                            },
                            "&.Mui-focused fieldset": {
                                "borderColor": "#4FECD7",
                            },
                        },
                        "& .MuiOutlinedInput-input": {
                            "color": "#FFFFFF",
                        },
                        "& .MuiInputLabel-root": {
                            "color": "rgba(255, 255, 255, 0.7)",
                        },
                    },
                )
                mui.Button(
                    "SEND",
                    variant="contained",
                    size="medium",
                    sx={
                        "backgroundColor": "#4FECD7",
                        "color": "#000000",
                        "minWidth": "80px",
                        "height": "40px",
                        "&:hover": {
                            "backgroundColor": "#3DD1BE",
                        },
                    },
                )
