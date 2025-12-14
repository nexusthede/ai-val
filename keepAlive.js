const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Val is alive.');
});

function keepAlive() {
  app.listen(process.env.PORT || 3000, () => {
    console.log('KeepAlive running on port ' + (process.env.PORT || 3000));
  });
}

module.exports = keepAlive;
