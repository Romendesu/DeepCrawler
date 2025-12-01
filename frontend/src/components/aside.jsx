import { showMore, chat, login, checkActivity, settings, logoutIcon } from "/src/assets/icons/aside/exportIcons";
import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Aside({isOpen, toggleBar}) {
    const {user, token, logout} = useContext(AuthContext)
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
                        <a href="/auth"><button><img src={login} /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Autentificate</p>
                    </div>
                ) : 
                (
                    <div className="intro-label">
                        <button onClick={logout}><img src={logoutIcon} /></button>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Cerrar Sesión</p>
                    </div>
                ) }
                
                {/* En caso de que el usuario  este autentificado, sale la foto de perfil del usuario */}
                {/*Se muestra unicamente si el usuario está autentificado*/}
                { token && (
                    <div className="intro-label">
                        <a href="/record"><button><img src={checkActivity} /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Ver actividad reciente</p>
                    </div>
                )}
                
                { token && (
                    <div className="intro-label">
                        <a href="/config"><button><img src={settings} /></button></a>
                        <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Ajustes</p>
                    </div>)
                }
            </div>
        </aside>
    )
}
