const { DataTypes } = require('sequelize');
const sequelize = require('../db'); // Importa la instancia de conexión

// Este modelo define la estructura de un mensaje dentro de una sesión de chat.

const ChatMessage = sequelize.define('ChatMessage', {
    // Clave primaria generada automáticamente
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
        allowNull: false
    },
    // Contenido del mensaje (puede ser largo para respuestas del asistente)
    content: {
        type: DataTypes.TEXT,
        allowNull: false,
    },
    // Rol del emisor: 'user' o 'assistant'
    role: {
        type: DataTypes.ENUM('user', 'assistant'),
        allowNull: false
    },
    // Clave foránea que enlaza este mensaje a una ChatSession (definida en index.js)
    // Sequelize automáticamente añade el campo 'ChatSessionId'
}, {
    // Nombre de la tabla en la base de datos
    tableName: 'ChatMessages',
    // Opciones para incluir timestamps (createdAt, updatedAt)
    timestamps: true 
});

module.exports = ChatMessage;