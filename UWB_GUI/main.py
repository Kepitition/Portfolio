import uwb3anchorstest # Assuming your GUI code is in uwb3anchorstest.py

def main():
    """
    Launches the UWB Trilateration Anchor Manager GUI application.
    """
    # The GUI initialization and main loop are contained within the uwb3anchorstest.py
    # script's 'if __name__ == "__main__":' block (or a main() function it calls).
    # By importing it, and assuming it has the __name__ == "__main__" guard,
    # the GUI will start when this script is run.

    # If uwb3anchorstest.py has a 'main()' function for its GUI, call it directly:
    uwb3anchorstest.main()

    # If uwb3anchorstest.py runs its GUI directly without a main() function,
    # simply importing it is enough:
    # (No explicit function call needed here if the GUI starts at the top level of the module)

if __name__ == "__main__":
    main()