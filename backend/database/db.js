// db.js
const { Sequelize } = require('sequelize');

// Crea o conecta a un archivo SQLite llamado "database.sqlite"
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: './bbdd.sqlite', // ruta del archivo
  logging: false 
});

module.exports = sequelize;
