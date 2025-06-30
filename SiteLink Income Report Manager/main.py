"""
SiteLink Financial Data Manager - Main Entry Point
"""
from gui.main_window import SiteLinkGUI

def main():
    """Main application entry point"""
    app = SiteLinkGUI()
    app.run()

if __name__ == "__main__":
    main()
