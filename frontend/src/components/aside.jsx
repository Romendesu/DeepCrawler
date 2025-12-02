import { showMore, chat, login, checkActivity, logoutIcon } from "/src/assets/icons/aside/exportIcons";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Aside({isOpen, toggleBar}) {
    const {user, token, logout} = useContext(AuthContext)

    // Función para decodificar la cadena Base64 y crear una Data URL
    const decodeBase64 = (base64String) => {
        if (!base64String || typeof base64String !== 'string') {
            return null;
        }
        if (base64String.startsWith('data:')) {
            return base64String;
        }
        // Asume un tipo de imagen genérico para la Data URL
        return `data:image/jpeg;base64,${base64String}`;
    }

    // 1. Obtener la URL de la imagen (Base64 decodificada)
    const profileImageUrl = decodeBase64(user?.pfp);

    // 🌟 FUNCIÓN CORREGIDA: Maneja el logout y la redirección a /
    const handleLogout = () => {
        logout(); // Cierra la sesión (borra token y user de localStorage/context)
        window.location.href = "/"; // Redirige al usuario a la página principal
    };

    return (
        <aside className={`aside ${isOpen ? "abierta" : "cerrada"}`}>
            <div className="intro-buttons">
                <div className="intro-buttons">
                    <button onClick={toggleBar}> <img src={showMore} alt="Agrandar la barra"/></button>
                </div>
            </div>
            <div className="intro-buttons">
                {/*Se muestra unicamente si el usuario está autentificado*/}
                { token && (
                    <div className="intro-label">
                        <a href="/"><button><img src={chat} alt="Iniciar conversación" /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Iniciar nueva conversación</p>
                    </div>
                    )
                } 
                {/* En caso de que el usuario no este autentificado, sale el icono del auth*/}
                { !token ? (
                    <div className="intro-label">
                        <a href="/auth"><button><img src={login} alt="Autenticarse" /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Autentificate</p>
                    </div>
                ) : 
                (
                    <div className="intro-label">
                        {/* 🌟 CAMBIO AQUÍ: Llamamos a la nueva función handleLogout */}
                        <button onClick={handleLogout}><img src={logoutIcon} alt="Cerrar Sesión" /></button>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Cerrar Sesión</p>
                    </div>
                ) }
                
                {/* Ver actividad reciente */}
                { token && (
                    <div className="intro-label">
                        <a href="/record"><button><img src={checkActivity} alt="Ver actividad reciente" /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Ver actividad reciente</p>
                    </div>
                )}
                
                {/* Enlace de Configuración (Ahora la Foto de Perfil) */}
                { token && (
                    <div className="intro-label">
                        {/* 2. El botón ahora muestra la PFP o un icono por defecto */}
                        <a href="/config">
                            <button>
                                {profileImageUrl ? (
                                    // Si existe la imagen de perfil, la mostramos
                                    <img 
                                        src={profileImageUrl} 
                                        alt={`${user?.username}'s profile`} 
                                        style={{ 
                                            width: '35px', 
                                            height: '35px', 
                                            objectFit: 'cover',
                                            borderRadius: '50px'
                                        }} 
                                    />
                                ) : (
                                    // Icono de usuario por defecto si no hay foto
                                    <svg viewBox="0 0 24 24" fill="currentColor" style={{ width: '80%', height: '80%' }}>
                                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                                    </svg>
                                )}
                            </button>
                        </a>
                        {/* 3. El texto es el nombre de usuario */}
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>{user?.username || "Perfil"}</p>
                    </div>)
                }
            </div>
        </aside>
    )
}