# RL-2000X Master PRO - Group 46 

![Banner Image](https://se-gitlab.inf.tu-dresden.de/robolab-spring/ws2022/group-046/-/raw/master/banner.jpg)

Der RL-2000X Master PRO auf Mission auf dem Planeten Curry.


# Aufteilung
* Robin: Robot
* Alex: Planet / Odo
* Dominik: Communication

Please see the individial journals for more information.

# Gettings started


## Environment

You might want to create a `src/.env` file to set the default values for the `SIMULATOR` and `DEBUG` variables.

### Example for development purposes:

```
SIMULATOR=True
DEBUG=True
```

### Using the simulator

Please switch to `sync-sim` branch to use the simulator.

The simulator also provides an optional web interface to view the positioning of the robot on the planet.

Setup the web interface by running the following commands:

```
cd src/simulator
npm install
node server.js
```

Now you can access the web interface at `http://localhost:3000`.

The web interface will display the robot during the run of `python main.py`.

Python can also be controlled via the web interface play/pause button.
