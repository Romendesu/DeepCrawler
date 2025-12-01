// router.js (MODIFICADO para usar el servidor Flask)

const express = require('express');
const router = express.Router();
// Necesitas un cliente HTTP para Node.js, como 'node-fetch' o 'axios'
// Si usas Node.js >= 18, puedes usar el fetch API global. Aquí usaremos 'axios' por ser común.
// Debes instalarlo: npm install axios
const axios = require('axios'); 

// URL del servicio Flask
const CRAWLER_API_URL = process.env.CRAWLER_API_URL || 'http://localhost:5000/api/crawler';

// POST /api/crawler (Ahora actúa como Proxy)
router.post('/', async (req, res) => {
    const prompt = (req.body && req.body.prompt) ? String(req.body.prompt) : '';
    
    if (!prompt) {
        return res.status(400).json({ error: 'Missing prompt in request body' });
    }

    try {
        // 1. Reenviar la solicitud al servidor Flask/Python
        const response = await axios.post(CRAWLER_API_URL, { prompt: prompt });
        
        // 2. Devolver la respuesta de Flask directamente al cliente
        // El body de la respuesta ya es el JSON generado por el Crawler.
        return res.json(response.data);

    } catch (error) {
        console.error('Proxy Error: Failed to connect to Python Crawler API (Flask):', error.message);
        
        // Capturar y devolver el error que viene del servidor Flask (si falló en el 4xx/5xx)
        if (error.response) {
            return res.status(error.response.status).json({
                error: 'Error del servicio Python Crawler',
                details: error.response.data || 'No se pudo contactar al servicio Flask.'
            });
        }
        
        // Error de conexión (Flask no está corriendo)
        return res.status(503).json({ 
            error: 'Servicio Python (Flask) no disponible.', 
            details: `Asegúrate de que 'app.py' esté corriendo en ${CRAWLER_API_URL}.`
        });
    }
});

module.exports = router;