from controller import Controller
import main


def run():
    client = main.init_client()
    con = Controller(client)
    con.begin()

if __name__ == '__main__':
    run()