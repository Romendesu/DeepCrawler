const { DataTypes } = require('sequelize');
const sequelize = require('../db'); // Importamos la instancia de conexión

// 🚨 CORRECCIÓN: Usamos sequelize.define() directamente.
// Esto evita el problema de inicialización del método Model.init()
const User = sequelize.define('User', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
        allowNull: false
    },
    username: { 
        type: DataTypes.STRING, 
        allowNull: false 
    },
    email: { 
        type: DataTypes.STRING, 
        allowNull: false, 
        unique: true 
    },
    password: { 
        type: DataTypes.STRING, 
        allowNull: false 
    },
    image: { 
        type: DataTypes.TEXT 
    }
}, {
    // Opciones del modelo
    tableName: 'users', // Conservamos tu nombre de tabla 'users'
    modelName: 'User', // Nombre lógico del modelo
    timestamps: true 
});

module.exports = User;