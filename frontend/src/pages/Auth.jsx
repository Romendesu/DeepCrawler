import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { PopUpContext } from "../context/PopUpContext";
import "../styles/auth.css";
import { signup, login as loginService } from "../services/authService";

export default function Auth() {
  const [isNewUser, setIsOpen] = useState(false);
  const toggleAuth = () => setIsOpen(!isNewUser);

  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const { showPopUp } = useContext(PopUpContext);

  const handleSignUp = async (e) => {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;
    const confirmPassword = form["confirm-password"].value;

    try {
      const data = await signup(username, email, password, confirmPassword);

      showPopUp({
        title: data.status === "success" ? "🚀 Éxito" : "❌ Error",
        subtitle: data.message,
        type: data.status === "success" ? "active" : "error",
      });

      if (data.status === "success") {
        form.reset();
        navigate("/"); // Redirige al home
      }
    } catch (err) {
      showPopUp({
        title: "❌ Error",
        subtitle: "No se ha podido conectar con el servidor",
        type: "error",
      });
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const form = e.target;
    const email = form.email.value;
    const password = form.password.value;

    try {
      const data = await loginService(email, password);

      showPopUp({
        title: data.status === "success" ? "🚀 Éxito" : "❌ Error",
        subtitle: data.message,
        type: data.status === "success" ? "active" : "error",
      });

      if (data.status === "success") {
        form.reset();
        login(data.data, data.token); // Guarda info en AuthContext
        navigate("/"); // Redirige al home
      }
    } catch (err) {
      showPopUp({
        title: "❌ Error",
        subtitle: "No se ha podido conectar con el servidor",
        type: "error",
      });
    }
  };

  return (
    <div className="auth-main">
      <div className="header-auth">
        <h1>DeepCrawler</h1>
      </div>

      <div className="main">
        <div className="intro-auth-container">
          <h1>Iniciar sesión o registrarte</h1>
          <p className="subindex">
            Accede o regístrate para consultar tus conversaciones anteriores y
            disfrutar de funciones adicionales.
          </p>
          <button className="auth-button" onClick={toggleAuth}>
            <p>{isNewUser ? "Inicie sesión" : "Regístrese"}</p>
          </button>
        </div>

        <div className={`auth-body ${isNewUser ? "login" : "signup"}`}>
          {!isNewUser ? (
            <form className="auth-form login" onSubmit={handleLogin}>
              <h1>Iniciar sesión</h1>
              <div className="text-field">
                <input
                  name="email"
                  type="text"
                  placeholder="Correo Electrónico"
                  required
                />
              </div>
              <div className="text-field">
                <input
                  name="password"
                  type="password"
                  placeholder="Contraseña"
                  required
                />
              </div>
              <a href="#">No me acuerdo de mi contraseña</a>
              <button type="submit" className="auth-button">
                <p>Enviar información</p>
              </button>
            </form>
          ) : (
            <form className="auth-form sign-up" onSubmit={handleSignUp}>
              <h1>Registrarte</h1>
              <div className="text-field">
                <input
                  name="username"
                  type="text"
                  placeholder="Nombre de usuario"
                  required
                />
              </div>
              <div className="text-field">
                <input
                  name="email"
                  type="text"
                  placeholder="Correo Electrónico"
                  required
                />
              </div>
              <div className="text-field">
                <input
                  name="password"
                  type="password"
                  placeholder="Contraseña"
                  required
                />
              </div>
              <div className="text-field">
                <input
                  name="confirm-password"
                  type="password"
                  placeholder="Confirmar contraseña"
                  required
                />
              </div>
              <button type="submit" className="auth-button">
                <p>Enviar información</p>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
