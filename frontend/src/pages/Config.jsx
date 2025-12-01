import Aside from "../components/aside.jsx";
import { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import styles from "../styles/components/config.module.css"


export default function ConversationRecord () {
  const {user, token, logout} = useContext(AuthContext);
  const [isOpen, setIsOpen] = useState(false);
  const toggleBar = () => setIsOpen(!isOpen);

  // Función para decodificar la cadena Base64 y crear una Data URL
  const decodeBase64 = (base64String) => {
    // Si la cadena está vacía o no es válida, devolvemos null o un placeholder
    if (!base64String || typeof base64String !== 'string') {
        return null;
    }

    if (base64String.startsWith('data:')) {
        return base64String;
    }

    // Suponemos que es una imagen JPEG por defecto si no tiene prefijo. 
    return `data:image/jpeg;base64,${base64String}`;
  }

  // Obtenemos la URL de datos de la imagen
  const profileImageUrl = decodeBase64(user?.pfp);
  
  // Nota: Usamos user?.pfp para evitar errores si el objeto 'user' es null al inicio.

  return (
    <>
      <Aside isOpen={isOpen} toggleBar={toggleBar} />
      <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
        <div className="header">
          <h1> DeepCrawler </h1>
        </div>
        <div className={styles.mainContainer} >
            <h1>Configuración</h1>
            {/* 1. Muestra la imagen usando la Data URL */}
            <p>
                {profileImageUrl ? (
                    <img 
                        src={profileImageUrl} 
                        alt={`${user.username}'s profile picture`} 
                        style={{ width: '100px', height: '100px', borderRadius: '50%', objectFit: 'cover' }} 
                    />
                ) : (
                    <span> No disponible</span>
                )}
            </p>

            {/* 2. Muestra los otros datos */}
            <p><strong>Nombre de usuario:</strong> {user?.username}</p>
            <p><strong>Correo Electrónico:</strong> {user?.email}</p>
            
            <form className={styles.changeForm}>
                <input name="username" placeholder="Cambiar nombre de usuario" type="text"></input>
                <input name="email" placeholder="Cambiar correo electrónico" type="text"></input>
                <input name="password" placeholder="Cambiar contraseña" type="text"></input>
            </form>
        </div>
      </main>
    </>
  )
}