const express = require("express");
const router = express.Router();
const User = require('../database/models/Users');
const { hashPassword, comparePassword} = require('../utils/encryption');
const { existEmail,imageToBase64 } = require('../utils/auxiliarFunctions');
const jwt = require("jsonwebtoken");
const JWTSECRET = "4lOw0S2p13BuT461nophDMTj9HeDw2YKc/UVkyvvK75gqUPQ1kPAcrcV+J8nQ2ZQiuR/KfoGagJmClKeFqg8oQ=="

// Registro de usuarios
router.post("/sing-up", async (req,res) => {
    console.log("Registrando al usuario")
    const {username, email, password, confirmPassword} = req.body;
    pfp = await imageToBase64();
    console.log("Parametros recibidos:", username, email, password, confirmPassword)
    // Paso 0: Verificar que hay algun campo
    if (!username || !email || !password || !confirmPassword) {
        console.log("No se ha proporcionado las credenciales...")
        return res.status(400).json({
                status: "error",
                message:"No se han completado todos los campos"
        });
    }
    // Paso 1: Verificar contraseñas
    if (password !== confirmPassword) {
        return res.status(400).json({
            status: "error",
            message: "Las contraseñas no coincides"
        });
    }
    // Paso 2: Acceso a la base de datos
    try {
        // Verificar la existencia del Email.
        if (await existEmail(email)) {
            console.log("El correo ingresado esta en la base de datos")
            return res.status(400).json({
                status: "error",
                message: "El correo ya está asociado a una cuenta"
            })
        }

        // Cifrar la contraseña
        const hashedPassword = await hashPassword(password);

        // Creacion del usuario en la base de datos
        const newUser = await User.create({
            username,
            email,
            password: hashedPassword,
            image: pfp
        })

        res.status(201).json({
            status: 'success',
            message: 'Usuario creado correctamente',
        });

    } catch (error) {
        console.log(error)
        res.status(500).json({
            status: 'error',
            message: 'Error del servidor al procesar la información'
        });
    }
})

// Ruta para el login de usuarios
router.post("/login", async(req,res) => {
    const {email, password} = req.body;
    console.log("Parametros recibidos:",email, password)
    // Verificamos que estan todos los datos
    if (!email || !password) {
        return res.status(400).json({
            status: "error",
            message:"No se han completado todos los campos"
        });
    }

    try {
        // Verificar que el usuario este dentro de la base de datos
        const user = await User.findOne({where:{email}});
        if (!user) {
            return res.status(400).json({status: "error", message:"El usuario no está registrado"})
        }

        // Comparamos contraseñas
        const correctPassword = await comparePassword(password, user.password);
        if (!correctPassword) {
            return res.status(400).json({status:"error", message:"La contraseña introducida no es correcta"});
        }

        // Creacion del token
        const token = jwt.sign(
            {
                id: user.id,
                username: user.username,
                email: user.email,
            },
            JWTSECRET,
            { expiresIn: "2h" }
        )
        return res.json({
            status: "success",
            message: `Inicio de sesión correcto, ¡Bienvenido ${user.username}!`,
            token,
            data: {
                id : user.id,
                username: user.username,
                email: user.email,
                pfp: user.image
            }
        })

    } catch (error) {
        console.log(error)
        return res.status(500).json({status:"error", message:"Error del servidor al procesar información"})
    }
})

// Exportar
module.exports = router;