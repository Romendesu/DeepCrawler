import { showMore, chat, login, register, checkActivity, settings } from "/src/assets/icons/aside/exportIcons";


export default function Aside({isOpen, toggleBar}) {
    
    /* Tareas a realizar: 
    1) Crear logica de ocultar y mostrar el menu -> Hecho
    2) Decorar la interfaz: -> Hecho
    3) Meter aparicion de texto para guiar al usuario: Proceso
    4) Enrutar cada opcion
    5) Meter iconos: Proceso
    */

    return (
        <aside className={`aside ${isOpen ? "abierta" : "cerrada"}`}>
            <div className="intro-buttons">
                <div className="intro-buttons">
                    <button onClick={toggleBar}> <img src={showMore} alt="Agrandar la barra"/></button>
                </div>
                <div className="intro-label">
                    <button><img src={chat} alt="Historial de mensajes" /></button>
                    <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Historial de mensajes</p>
                </div>
            </div>
            <div className="intro-buttons">
                <div className="intro-label">
                    <a><button><img src={login} /></button></a>
                    <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Iniciar Sesión</p>
                </div>
                <div className="intro-label">
                    <a><button><img src={register} /></button></a>
                    <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Registrarte</p>
                </div>
                <div className="intro-label">
                    <button><img src={checkActivity} /></button>
                    <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Ver actividad reciente</p>
                </div>
                <div className="intro-label">
                    <button><img src={settings} /></button>
                    <p className={`intro-text ${isOpen ? "abierta" : "cerrada"}`}>Ajustes</p>
                </div>
            </div>
        </aside>
    )
}