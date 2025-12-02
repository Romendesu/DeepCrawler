const sequelize = require('./db'); // 1. Obtiene la instancia de conexión
const User = require('./models/Users'); // 2. Importa el modelo User
const ChatSession = require('./models/Chat');   // 3. Importa el modelo de Sesión (usando Chat.js)
const ChatMessage = require('./models/ChatMessage'); // 4. Importa el modelo de Mensajes

// --- Definición de Asociaciones ---

// ASOCIACIONES 1: USUARIO <-> SESIÓN (1:N)
// Un usuario (User) tiene muchas sesiones de chat (ChatSession).
User.hasMany(ChatSession, {
  foreignKey: 'UserId', 
  onDelete: 'CASCADE'  
});

// Una sesión (ChatSession) pertenece a un usuario (User).
ChatSession.belongsTo(User, {
  foreignKey: 'UserId'
});


// ASOCIACIONES 2: SESIÓN <-> MENSAJES (1:N)
// Una sesión (ChatSession) tiene muchos mensajes (ChatMessage).
ChatSession.hasMany(ChatMessage, {
    foreignKey: 'ChatSessionId', 
    onDelete: 'CASCADE'
});

// Un mensaje (ChatMessage) pertenece a una sesión (ChatSession).
ChatMessage.belongsTo(ChatSession, {
    foreignKey: 'ChatSessionId'
});


// Exporta la instancia de Sequelize y TODOS los modelos asociados,
// con los nombres que espera el router (User, ChatSession, ChatMessage).
module.exports = {
  sequelize,
  User,
  ChatSession, 
  ChatMessage 
};