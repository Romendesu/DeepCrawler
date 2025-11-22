import Aside from "../components/aside";
import "../styles/home.css"
import { paperPlane, toolsKit } from "../assets/icons/home/exportIcons";
import { useState } from "react";

export default function Home() {
  const [isOpen, setIsOpen] = useState(false);
  const toggleBar = () => setIsOpen(!isOpen);

  return (
    <>
      <Aside isOpen={isOpen} toggleBar={toggleBar} />

      <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
        <div className="header">
          <h1> DeepCrawler </h1>
        </div>
        <div className="question-body">
          <h1>Hola, Nombre de usuario</h1>
          <form className="input">
            <input placeholder="Pregunta a DeepCrawler"></input>
            <div className="tools-kit">
              <button className="button-with-text">
                <img src={toolsKit} alt="Herramientas"/>
                <p>Ver mas herramientas</p> 
              </button>
              {/* Deberia abrirse un desplegable por aqui con todos los modelos de IA*/}
              <button className="button-without-text">
                <img src={paperPlane} alt="Enviar mensaje"/>
              </button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}
