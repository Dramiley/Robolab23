const express = require('express');
const app = express()
const port = 3000
const fs = require('fs');


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

app.use(express.static('./static'));

app.listen(port, () => {
    console.log(`Simulator started at http://localhost:${port}`)
})
