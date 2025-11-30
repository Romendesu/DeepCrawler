const sequelize = require('./db');
const User = require('./models/Users');

async function syncDB() {
  try {
    await sequelize.sync();
    console.log('Base de datos y tablas listas');
  } catch (err) {
    console.error('Error sincronizando la base de datos:', err);
  }
}

module.exports = syncDB;
