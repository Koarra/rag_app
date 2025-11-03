"""
Main entry point for Article Detective application.
Can be run directly or imported for additional functionality.
"""

import logging
import os
import traceback
from pathlib import Path
import streamlit as st

# Import the main application
from streamlit_app import main as streamlit_main

LOG = logging.getLogger(__name__)


class ArticleDetectiveApp:
    """Article Detective application wrapper with helper functions."""

    def __init__(self, asset_folder=None, config_file=None):
        """Initialize the application."""
        # Set asset folder based on environment
        if asset_folder:
            self.asset_folder = Path(asset_folder)
        elif "DOMINO_DATASETS_DIR" in os.environ and "DOMINO_PROJECT_NAME" in os.environ:
            # Running on Domino
            self.asset_folder = (
                Path(os.environ["DOMINO_DATASETS_DIR"])
                / "local"
                / os.environ["DOMINO_PROJECT_NAME"]
                / "articledetective_assets"
            )
        else:
            # Running locally
            self.asset_folder = Path("articledetective_assets")

        self.asset_folder.mkdir(parents=True, exist_ok=True)
        self.config_file = Path(config_file) if config_file else None

    def local_css(self, file_name):
        """Load custom CSS file."""
        css_path = Path(__file__).parent / file_name
        if not css_path.exists():
            LOG.warning(f"CSS file not found: {css_path}")
            return
        try:
            with open(css_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            LOG.error(f"Error loading CSS: {e}")

    def configure_page(self):
        """Configure the Streamlit page with custom settings."""
        st.set_page_config(
            page_title="Article Detective",
            page_icon="🔍",
            initial_sidebar_state="expanded",
            layout="wide",
        )

        # Load custom CSS if style.css exists
        if (Path(__file__).parent / "style.css").exists():
            self.local_css("style.css")

    def run(self):
        """Run the main application."""
        try:
            # Configure page if not already configured
            if not st._is_running_with_streamlit:
                self.configure_page()

            # Run the main streamlit app
            streamlit_main()

        except Exception as e:
            LOG.error(f"Application error: {traceback.format_exc()}")
            st.error(f"An error occurred: {str(e)}")
            raise e


def main():
    """Main entry point."""
    try:
        # Check if running on Domino
        if "DOMINO_DATASETS_DIR" in os.environ:
            LOG.info("Running on Domino Data Lab")
            app = ArticleDetectiveApp()
            app.run()
        else:
            # Running locally - just run streamlit_main directly
            LOG.info("Running locally")
            streamlit_main()

    except Exception as e:
        LOG.error(traceback.format_exc())
        st.error(f"Application failed to start: {str(e)}")
        raise e


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
