const { Sequelize } = require('sequelize');

// Crea o conecta a un archivo SQLite llamado "bbdd.sqlite"
// Se utiliza la sintaxis del constructor para SQLite, ya que no necesita host, usuario o password.
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: './bbdd.sqlite', // Ruta del archivo de la base de datos
    logging: false // Deshabilita el logging en consola de las consultas SQL
});

// Exportamos la instancia de Sequelize directamente para que los modelos puedan usarla.
module.exports = sequelize;