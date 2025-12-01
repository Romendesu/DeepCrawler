import Aside from "../components/aside";
import { AuthContext } from "../context/AuthContext";
import "../styles/home.css"
import { paperPlane, toolsKit } from "../assets/icons/home/exportIcons";
import { useState, useContext } from "react";

export default function Home() {
  const [isOpen, setIsOpen] = useState(false);
  const toggleBar = () => setIsOpen(!isOpen);
  const {user, token, logout} = useContext(AuthContext)

  const [prompt, setPrompt] = useState('');
  // 1. Mantener el estado inicial de bienvenida
  const initialWelcomeText = token ? `¡Bienvenido! ${user.username}` : '¡Hola! Bienvenido a DeepCrawler';
  const [welcomeText, setWelcomeText] = useState(initialWelcomeText);
  
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!prompt || prompt.trim().length === 0) return;
    
    // Muestra el prompt en el título mientras busca
    setWelcomeText(`Buscando: ${prompt}...`);
    
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:3000/api/crawler', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt })
      });
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.error || 'Error en la petición');
        setResponse(null);
        setWelcomeText(initialWelcomeText); 
      } else {
        setResponse(data);
        
        // LÓGICA CLAVE: Actualizar el título de bienvenida con el texto limpio
        if (data.response && typeof data.response === 'string') {
            // Caso 1: La respuesta es la cadena limpia (ideal)
            setWelcomeText(data.response);
        } else if (data.response && data.response.summary) {
            // Caso 2: La respuesta es un objeto con campo 'summary'
            setWelcomeText(data.response.summary);
        } else if (data.response) {
            // Fallback: si existe respuesta pero no tiene el formato esperado
            setWelcomeText(`Respuesta lista para: ${prompt}`);
        } else {
            // Fallback: si no hay 'response' en el JSON, mostrar el prompt enviado
            setWelcomeText(prompt);
        }
      }
    } catch (err) {
      setError(String(err));
      setResponse(null);
      setWelcomeText(initialWelcomeText); 
    }
    setLoading(false);
  }

  // --- Lógica para el cambio dinámico de etiqueta ---
  // Determina qué etiqueta usar: <h1> si no hay respuesta final, <p> si la hay.
  // También determina la clase CSS: 'welcome-title' para el h1 inicial, 'response' para el p.
  const isResponseReady = response && (typeof response.response === 'string' || response.response?.summary);
  const ResponseDisplayTag = isResponseReady ? 'p' : 'h1';
  const ResponseCssClass = isResponseReady ? 'response' : 'welcome-title';

  return (
    <>
      <Aside isOpen={isOpen} toggleBar={toggleBar} />

      <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
        <div className="header">
          <h1> DeepCrawler </h1>
        </div>
        <div className="question-body">
          {/* Implementación de la etiqueta dinámica */}
          <ResponseDisplayTag className={ResponseCssClass}>
            {welcomeText}
          </ResponseDisplayTag>
          
          <form className="input" onSubmit={handleSubmit}>
            <input 
              placeholder="Pregunta a DeepCrawler" 
              value={prompt} 
              onChange={(e) => setPrompt(e.target.value)} 
              disabled={loading}
            />
            <div className="tools-kit">
              <button type="button" className="button-with-text" onClick={() => { /* placeholder for tools */ }} disabled={loading}>
                <img src={toolsKit} alt="Herramientas"/>
                <p>Ver mas herramientas</p> 
              </button>
              <button type="submit" className="button-without-text" disabled={loading}>
                <img src={paperPlane} alt="Enviar mensaje"/>
              </button>
            </div>
          </form>

          <div className="response-area">
            {loading && <p>Buscando...</p>}
            {error && <p className="error">Error: {error}</p>}
            
            {/* El área de respuesta ahora está limpia, mostrando solo el estado y errores. */}
          </div>
        </div>
      </main>
    </>
  );
}