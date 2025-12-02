const { DataTypes } = require('sequelize');
const sequelize = require('../db'); // Importamos la instancia de conexión

// Definición del modelo Chat (Sesión de Chat)
const ChatSession = sequelize.define('Chat', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
        allowNull: false
    },
    title: { 
        type: DataTypes.STRING, 
        allowNull: false,
        defaultValue: 'Nueva Conversación'
    },
    // 🚨 CORRECCIÓN: Eliminamos 'content' y 'context' si no son necesarios, 
    // o hacemos que permitan nulos. Aquí eliminamos los campos innecesarios
    // ya que el contenido se guarda en ChatMessage.
}, {
    tableName: 'Chats', 
    modelName: 'ChatSession', 
    timestamps: true 
});

module.exports = ChatSession;