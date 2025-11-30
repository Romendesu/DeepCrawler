const User = require('../database/models/Users'); 
const fs = require('fs');
const path = require('path');

/**
 * Convierte una imagen a Base64
 * @param {Object} options
 * @param {"local"|"server"} options.source - 'local' para imagen por defecto, 'server' para imagen subida
 * @param {Buffer} [options.buffer] - buffer de la imagen si source='server'
 * @returns {Promise<string|null>} - Base64 de la imagen o null si falla
 */
async function imageToBase64({ source = "local", buffer = null } = {}) {
  try {
    let imageBuffer;

    if (source === "local") {
      // Imagen local por defecto
      const fullPath = path.resolve(__dirname, "../assets/img/defaultpfp.png");
      imageBuffer = fs.readFileSync(fullPath);
    } else if (source === "server") {
      if (!buffer) throw new Error("Debe proporcionar un buffer para source='server'");
      imageBuffer = buffer;
    } else {
      throw new Error("source inválido. Debe ser 'local' o 'server'");
    }

    return imageBuffer.toString("base64");
  } catch (err) {
    console.error("Error al convertir imagen a Base64:", err);
    return null;
  }
}

// Verificar si un email ya existe
async function existEmail(email) {
  const user = await User.findOne({ where: { email } });
  return user !== null;
}

module.exports = { imageToBase64, existEmail };
