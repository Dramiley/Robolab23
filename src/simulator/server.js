const express = require('express');
const app = express()
const port = 3000
const fs = require('fs');

const http = require('http');
const server = http.createServer(app);
const {Server} = require("socket.io");
const io = new Server(server);

let available_planets = fs.readdirSync('./planets').filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''))

app.get('/history', (req, res) => {
    res.send(fs.readFileSync('./history.json', 'utf8'));
});
app.get('/planet', (req, res) => {
    // read file ../planets/current_planet.json into var
    let name = fs.readFileSync('./planets/current.txt', 'utf8')

    // read file ../planets/{planetName}.def.json into var
    let def = JSON.parse(fs.readFileSync('./planets/' + name + '.json', 'utf8'))

    // remove the paths from the def
    def.paths = undefined;

    // output them
    res.send({name, def});
});
app.get('/planets', (req, res) => {
    res.send(available_planets);
})

app.post('/planet', (req, res) => {
    // write the passed name to ./planets/current_planet.json if it exists
    // otherwise return 404
    let name = req.query.name
    if (!available_planets.includes(name)) {
        res.status(404).send('Planet ' + name + ' not found. Available planets: ' + available_planets.join(', '));
    } else {
        fs.writeFileSync('./planets/current.txt', name, 'utf8')

        // empty history
        fs.writeFileSync('./history.json', '[{"type":"communication.log","message":"Set planet to ' + name + '.","color":"success"}]', 'utf8')
        res.send('Planet set to ' + name);
    }
});

app.use(express.static('./static'));
app.use(express.static('./planets'));


server.listen(port, () => {
    console.log(`Simulator started at http://localhost:${port}`)
});

// every time the history file changes, send the new data to all clients
fs.watchFile('./history.json', {interval: 100}, (curr, prev) => {
    io.emit('history', true); //fs.readFileSync('./history.json', 'utf8')
});

const {exec} = require("child_process");
app.get('/run/start', (req, res) => {
    console.log('Starting python script');
    try {
        exec('python3 ../main.py');

        res.send('Started python script');
    } catch (e) {
        res.send('Could not start: ' + e);
    }
});
app.get('/run/deploy', (req, res) => {
    try {
        exec('python3 ../deploy.py');

        res.send('Deployed python script');
    } catch (e) {
        res.send('Could not deploy: ' + e);
    }
})

app.get('/run/stop', (req, res) => {
    try {
        // stop python script
        exec('pkill -f main.py', (error, stdout, stderr) => {

            // get current directory path
            let path = __dirname + '/'

            // find all files that end with .lock or have a name longer than 40 characters
            let files = fs.readdirSync(__dirname).filter(f => f.endsWith('.lock') || f.length > 40)

            // delete all files that match the criteria
            files.forEach(f => {
                console.log('Deleting ' + path + f)
                fs.unlinkSync(path + f)
            })

            res.send('Stopped python script');
        })
    } catch (e) {
        res.send('Could not stop: ' + e);
    }

});
