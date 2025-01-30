import streamlit as st
from app.dashboard import init_dashboard


def main():
    st.set_page_config(
        page_title="DOBA-S Dashboard", layout="wide", initial_sidebar_state="expanded"
    )

    init_dashboard()


if __name__ == "__main__":
    main()
