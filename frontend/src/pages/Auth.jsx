import { useState } from "react";
import {User} from "../assets/icons/auth/exportIcons"
import "../styles/auth.css"

export default function Auth() {
  const [isNewUser, setIsOpen] = useState(false);
  const toggleAuth = () => setIsOpen(!isNewUser);

  return (
    <>
    <div className="auth-main">
    <div className="header-auth">
      <h1>DeepCrawler</h1>
    </div>
      <div className="main">
        <div className="intro-auth-container">
          <h1>Iniciar sesión o registrarte</h1>
          <p className="subindex">
              Accede o regístrate para consultar tus conversaciones anteriores y disfrutar de funciones adicionales.
          </p>
          <button className="auth-button" onClick={toggleAuth}><p>{isNewUser ? "Inicie sesión" : "Registrese"}</p></button>
        </div>
        <div className={`auth-body ${isNewUser ? "login" : "signup"}`}>
          {/*Formulario manejado con un condicional */}
          {!isNewUser ?
          (
            <form className="auth-form login">
              {/* Inicio de sesión */}
              <h1>Iniciar sesion</h1>
              <div className="text-field">
                <input name="username" type="text" placeholder="Nombre de usuario"></input>
              </div>
              <div className="text-field">
                <input name="username" type="text" placeholder="Contraseña"></input>
              </div>
              <a href="#">No me acuerdo de mi contraseña</a>
            </form>
          ) : 
          (
            <form className="auth-form sign-up">
              {/* Registro de usuarios*/}
              <h1>Registrarte</h1>
              <div className="text-field">
                <input name="username" type="text" placeholder="Nombre de usuario"></input>
              </div>
              <div className="text-field">
                <input name="email" type="text" placeholder="Correo Electrónico"></input>
              </div>
              <div className="text-field">
                <input name="password" type="text" placeholder="Contraseña"></input>
              </div>
              <div className="text-field">
                <input name="confirm-password" type="text" placeholder="Confirmar contraseña"></input>
              </div>
            </form>
          )}
        </div>
        <button className="auth-button">
          <p>Enviar información</p>
        </button>
      </div>
    </div>
    </>
  );
}
