from controller2 import Controller, Position
from planet import Direction
from planet import Planet
import main


def run():
    test_robo_rot()
    # con.planet = Planet()
    # con.begin()

def test_robo_rot():
    client = main.init_client()
    con = Controller(client)
    con.last_position = Position(0, 0, Direction(0))
    con.rotate_robo_dir(90)


if __name__ == '__main__':
    run()