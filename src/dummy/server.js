const express = require('express');
const app = express()
const port = 3000
const fs = require('fs');

app.get('/position', (req, res) => {
    res.send(fs.readFileSync('./position.json', 'utf8'));
});

app.use(express.static('static'));

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})
