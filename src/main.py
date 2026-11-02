from src.controller import PongGame


def main() -> None:
    # Create an instance of the game and start the main loop.
    game = PongGame()
    game.run()


if __name__ == "__main__":
    main()
