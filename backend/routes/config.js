const express = require('express');
const router = express.Router();
const User = require('../database/models/Users'); // Asegura que esta ruta es correcta
const { imageToBase64, existEmail } = require('../utils/auxiliarFunctions'); 
const { body, validationResult } = require('express-validator');
const bcrypt = require('bcrypt');
const multer = require('multer');

// --- 1. CONFIGURACIÓN DE MULTER ---
const storage = multer.memoryStorage();
const upload = multer({ 
    storage: storage,
    limits: { 
        fileSize: 5 * 1024 * 1024 // Limite de 5MB
    },
    fileFilter: (req, file, cb) => {
        if (file.mimetype.startsWith('image/')) {
            cb(null, true);
        } else {
            cb(new Error('Solo se permiten archivos de imagen.'), false);
        }
    }
});


// --- 2. VALIDACIÓN DE ENTRADA ---
const validateUpdate = [
    body('username')
        .optional()
        .isLength({ min: 3 }).withMessage('El nombre de usuario debe tener al menos 3 caracteres.'),
    
    body('email')
        .optional()
        .isEmail().withMessage('El formato del correo electrónico es inválido.'),
        
    body('password')
        .optional()
        .isLength({ min: 6 }).withMessage('La contraseña debe tener al menos 6 caracteres.'),
];


// --- 3. ENDPOINT PUT /api/users/:userId (LÓGICA DE ACTUALIZACIÓN) ---

router.put('/:userId', upload.single('pfp'), validateUpdate, async (req, res) => {
    const { userId } = req.params;
    
    if (req.fileValidationError) {
        return res.status(400).json({ error: req.fileValidationError });
    }
    
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ error: errors.array()[0].msg });
    }

    try {
        const userToUpdate = await User.findByPk(userId);

        if (!userToUpdate) {
            return res.status(404).json({ error: 'Usuario no encontrado.' });
        }
        
        const updates = {};
        
        // Procesar Username
        if (req.body.username && req.body.username !== userToUpdate.username) {
            updates.username = req.body.username;
        }

        // Procesar Email
        if (req.body.email && req.body.email !== userToUpdate.email) {
            if (await existEmail(req.body.email)) {
                return res.status(400).json({ error: 'Este correo electrónico ya está en uso.' });
            }
            updates.email = req.body.email;
        }

        // Procesar Contraseña
        if (req.body.password) {
            const salt = await bcrypt.genSalt(10);
            updates.password = await bcrypt.hash(req.body.password, salt);
        }
        
        // Procesar Foto de Perfil (PFP)
        if (req.file) {
            const base64Image = await imageToBase64({ 
                source: "server", 
                buffer: req.file.buffer 
            });
            
            if (base64Image) {
                // 🚨 CORRECCIÓN: Usamos 'image' para coincidir con el modelo de Sequelize
                updates.image = base64Image; 
            } else {
                console.warn("Advertencia: No se pudo convertir la imagen subida a Base64.");
            }
        }
        
        // Aplicar los cambios
        if (Object.keys(updates).length === 0) {
             const currentUser = userToUpdate.toJSON();
             delete currentUser.password; 
             // Si el campo de la DB se llama 'image', asegúrate de devolverlo también como 'pfp' 
             // o cambiar el frontend para que lea 'image'.
             // Por consistencia con el frontend que probablemente espera 'pfp', asignamos el valor de 'image' a 'pfp' para el retorno.
             // Sin embargo, para la DB, usamos 'image'.
             return res.status(200).json({ 
                message: 'No se encontraron cambios para actualizar.', 
                user: currentUser
            });
        }
        
        await userToUpdate.update(updates);
        
        // Devolver el usuario actualizado
        const updatedUser = userToUpdate.toJSON();
        delete updatedUser.password; 
        
        // Aseguramos que el objeto retornado al frontend use el campo 'pfp' 
        // para la foto, aunque en la DB se llame 'image'.
        updatedUser.pfp = updatedUser.image;
        delete updatedUser.image; 

        return res.status(200).json({ 
            message: 'Perfil actualizado con éxito.', 
            user: updatedUser 
        });

    } catch (err) {
        if (err instanceof multer.MulterError) {
             return res.status(400).json({ error: `Error de archivo: ${err.message}` });
        }
        console.error('Error al actualizar el perfil:', err);
        return res.status(500).json({ error: 'Error interno del servidor al actualizar el perfil.' });
    }
});

module.exports = router;