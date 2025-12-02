const express = require('express');
const router = express.Router();
const axios = require('axios'); 
const { literal } = require('sequelize'); 

// Importación de modelos
const { ChatSession, ChatMessage, User } = require('../database'); 

// URL del servicio Flask
const CRAWLER_API_URL = process.env.CRAWLER_API_URL || 'http://localhost:5000/api/crawler';


// =======================================================
// --- POST /api/chats: CREAR O CONTINUAR CHAT ---
// =======================================================
router.post('/', async (req, res) => {
    const { prompt, sessionId, userEmail } = req.body;
    
    if (!ChatSession || !ChatMessage || !User) {
        console.error("ERROR CRÍTICO: Modelos de Sequelize no definidos. Revisar '../database/index.js'.");
        return res.status(500).json({ error: 'Internal Server Error', details: 'Falló la inicialización de la base de datos (Modelos no encontrados).' });
    }
    
    if (!prompt || !userEmail) {
        return res.status(400).json({ error: 'Missing prompt or userEmail in request body' });
    }
    
    let currentSession = null;
    
    try {
        // 1. Encontrar el usuario
        const user = await User.findOne({ where: { email: userEmail } });
        if (!user) {
            console.warn(`Usuario no encontrado con email: ${userEmail}`);
            return res.status(404).json({ error: 'User not found.' });
        }
        
        // 2. Sesión nueva o existente
        if (sessionId) {
            currentSession = await ChatSession.findByPk(sessionId);
            if (!currentSession) {
                return res.status(404).json({ error: 'Chat session not found.' });
            }
        } else {
            currentSession = await ChatSession.create({ 
                title: prompt.substring(0, 100),
                UserId: user.id
            });
        }

        // 3. Guardar el prompt del usuario
        await ChatMessage.create({ 
            content: prompt,
            role: 'user',
            ChatSessionId: currentSession.id
        });

        // 4. Llamar al servicio Flask
        const response = await axios.post(CRAWLER_API_URL, { prompt: prompt });
        const crawlerData = response.data;

        // 🚨 5. EXTRAER SOLO LA RESPUESTA DEL MODELO (CORREGIDO) 🚨
        let assistantResponseContent = 'No se recibió respuesta del crawler.';

        // Caso A: La respuesta está en la raíz (ej: { response_text: "..." })
        if (crawlerData.response_text) {
            assistantResponseContent = crawlerData.response_text;
        } 
        // Caso B: La respuesta está anidada dentro de 'response' (ej: { response: { response_text: "..." } })
        else if (crawlerData.response && crawlerData.response.response_text) {
            assistantResponseContent = crawlerData.response.response_text;
        }
        // Caso C: 'response' es un string directo (menos común)
        else if (crawlerData.response && typeof crawlerData.response === 'string') {
            assistantResponseContent = crawlerData.response;
        }
        // Fallback: Si no se encuentra texto limpio, guardamos el JSON completo por seguridad (pero esto es lo que queremos evitar)
        else {
            console.warn("Formato de respuesta desconocido del Crawler. Guardando JSON crudo.");
            assistantResponseContent = JSON.stringify(crawlerData); 
        }
        
        // 6. Guardar la respuesta del asistente (LIMPIA)
        await ChatMessage.create({ 
            content: assistantResponseContent,
            role: 'ai', // Usamos 'ai' o 'assistant', pero 'ai' parece ser el rol usado en el frontend
            ChatSessionId: currentSession.id
        });
        
        // 7. Devolver toda la conversación
        const messages = await ChatMessage.findAll({
            where: { ChatSessionId: currentSession.id },
            order: [['createdAt', 'ASC']]
        });

        return res.json({
            crawlerResponse: crawlerData, 
            sessionId: currentSession.id,
            messages: messages,
            sessionTitle: currentSession.title
        });

    } catch (error) {
        console.error('Error in POST /api/chats:', error.message);
        
        if (error.response) {
            return res.status(error.response.status).json({
                error: 'Error del servicio Python Crawler',
                details: error.response.data || 'No se pudo contactar al servicio Flask.'
            });
        }
        
        return res.status(500).json({ 
            error: 'Internal Server Error o Servicio Flask no disponible.', 
            details: error.message 
        });
    }
});


// =======================================================
// --- GET /api/chats/history: CARGAR HISTORIAL DE SESIONES ---
// =======================================================
router.get('/history', async (req, res) => {
    const userEmail = req.query.email; 

    if (!ChatSession || !User) {
        console.error("ERROR CRÍTICO: Modelos de Sequelize no definidos.");
        return res.status(500).json({ error: 'Internal Server Error', details: 'Falló la inicialización de la base de datos (Modelos no encontrados).' });
    }

    if (!userEmail) {
        return res.status(400).json({ error: 'Missing user email.' });
    }

    try {
        const user = await User.findOne({ where: { email: userEmail } });

        if (!user) {
            return res.status(404).json({ error: 'User not found.' });
        }

        const history = await ChatSession.findAll({
            where: { UserId: user.id },
            attributes: [
                'id', 
                'title', 
                'createdAt',
                [
                    literal(`(
                        SELECT content
                        FROM ChatMessages AS CM
                        WHERE CM.ChatSessionId = Chat.id
                        ORDER BY CM.createdAt DESC
                        LIMIT 1
                    )`),
                    'lastMessageContent'
                ]
            ],
            order: [['createdAt', 'DESC']]
        });

        return res.json(history);

    } catch (error) {
        console.error('Error fetching chat history:', error);
        return res.status(500).json({ error: 'Internal server error while fetching history.' });
    }
});


// =======================================================
// --- GET /api/chats/:sessionId: CARGAR SESIÓN ESPECÍFICA ---
// =======================================================
router.get('/:sessionId', async (req, res) => {
    const sessionId = req.params.sessionId;

    if (!ChatSession || !ChatMessage) {
        console.error("ERROR CRÍTICO: Modelos de Sequelize no definidos.");
        return res.status(500).json({ error: 'Internal Server Error', details: 'Falló la inicialización de la base de datos (Modelos no encontrados).' });
    }

    try {
        const session = await ChatSession.findByPk(sessionId);

        if (!session) {
            return res.status(404).json({ error: 'Chat session not found.' });
        }

        const messages = await ChatMessage.findAll({
            where: { ChatSessionId: sessionId },
            order: [['createdAt', 'ASC']]
        });
        
        return res.json({
            sessionId: session.id,
            sessionTitle: session.title,
            messages: messages,
        });

    } catch (error) {
        console.error('Error fetching single chat session:', error);
        return res.status(500).json({ error: 'Internal server error while fetching session.' });
    }
});


module.exports = router;