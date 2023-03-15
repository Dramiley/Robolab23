# RoboLab Spring Template

Template for the RoboLab course in spring which is conducted by the Systems Engineering Group at the Department of
Computer Science, TU Dresden.

* Acts as a base repository that groups clone and then set the upstream to their assigned repo afterwards.
* Provides scripts to speed up and automate the process of deploying as well as executing Python code on LEGO MINDSTORMS
  EV3 robots running the customized, Debian based operating system.
* Includes the programming interface which is used to check parts of the students solutions in the final exam.

## Getting Started

You might want to create a `src/.env` file to set the default values for the `SIMULATOR` and `DEBUG` variables.

### Example for development purposes:

```
SIMULATOR=True
DEBUG=True
```

### Using the simulator

The simulator also provides an optional web interface to view the positioning of the robot on the planet.

Setup the web interface by running the following commands:

```
cd src/simulator
npm install
node server.js
```

Now you can access the web interface at `http://localhost:3000`.

The web interface will display the robot during the run of `python main.py`.

## Help

Please consult the [RoboLab Docs](https://robolab.inf.tu-dresden.de/spring).
We provide extensive sections about this template, the Deploy-Script and the interfaces.

