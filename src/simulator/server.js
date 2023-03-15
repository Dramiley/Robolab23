const express = require('express');
const app = express()
const port = 3000
const fs = require('fs');

let available_planets = fs.readdirSync('./planets').filter(f => f.endsWith('.def.json')).map(f => f.replace('.def.json', ''))

app.get('/history', (req, res) => {
    res.send(fs.readFileSync('./history.json', 'utf8'));
});
app.get('/planet', (req, res) => {
    // read file ../planets/current_planet.json into var
    let name = fs.readFileSync('./planets/current_planet.txt', 'utf8')

    // read file ../planets/{planetName}.def.json into var
    let def = JSON.parse(fs.readFileSync('./planets/' + name + '.def.json', 'utf8'))

    // output them
    res.send({def, name});

});
app.get('/planets', (req, res) => {
    res.send(available_planets);
})

app.post('/planet', (req, res) => {
    // write the passed name to ./planets/current_planet.json if it exists
    // otherwise return 404
    let name = req.query.name
    let file_name = './planets/' + name + '.def.json'
    if (!available_planets.includes(name)) {
        res.status(404).send('Planet ' + name + ' not found. Available planets: ' + available_planets.join(', '));
    } else {
        fs.writeFileSync('./planets/current_planet.txt', name, 'utf8')

        // empty history
        fs.writeFileSync('./history.json', '[{"type":"communication.log","message":"Set planet to ' + name + '.","color":"success"}]', 'utf8')
        res.send('Planet set to ' + name);
    }
});

app.use(express.static('./static'));

app.listen(port, () => {
    console.log(`Simulator started at http://localhost:${port}`)
})
