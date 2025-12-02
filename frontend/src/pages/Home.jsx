import Aside from "../components/aside";
import { AuthContext } from "../context/AuthContext";
import "../styles/home.css"
import { paperPlane, toolsKit } from "../assets/icons/home/exportIcons";
import { useState, useContext, useEffect, useRef } from "react";
import { useParams } from 'react-router-dom';

// 🚨 FUNCIÓN CLAVE: Extrae response_text del JSON si el rol es 'ai' 🚨
// Esta versión es la más robusta contra problemas de doble escape (\n, \", etc.)
const getMessageContent = (msg) => {
    // 1. Caso base: No es AI, o no es una cadena que parezca JSON.
    if (msg.role !== 'ai' || typeof msg.content !== 'string') {
        return msg.content;
    }

    let contentToParse = msg.content;
    let extractedText = null;

    // --- Primer intento de limpieza: Preparación para JSON.parse ---
    
    // 1. Reemplazar escapes de comillas internas (\\") por comillas simples (")
    contentToParse = contentToParse.replace(/\\"/g, '"');
    
    // 2. Eliminar saltos de línea crudos (\r\n, \n, \r) que rompen JSON.parse
    contentToParse = contentToParse.replace(/(\r\n|\n|\r)/gm, '').trim();

    // 3. Si la cadena resultante comienza y termina con comillas (indicando que es un string JSON dentro de un string), quitar la capa exterior.
    if (contentToParse.startsWith('"') && contentToParse.endsWith('"')) {
        contentToParse = contentToParse.slice(1, -1);
    }
    
    // 4. Limpieza de escapes Unicode (como \u000a para \n, \u0022 para comillas)
    contentToParse = contentToParse.replace(/\\u000a/g, '\n').replace(/\\u0022/g, '"');
    
    // --- Intento de Parseo ---
    try {
        const responseJson = JSON.parse(contentToParse);
        extractedText = responseJson.response_text;
    } catch (e) {
        // Si el parseo falla, intentamos una última limpieza de backslashes excesivos.
        console.error("Fallo de JSON.parse, intentando limpieza final.", e);
        
        try {
            // Intentar una limpieza final muy agresiva
            const finalCleanedContent = msg.content
                .replace(/\\n/g, '')     // Eliminar escapes de salto de línea internos
                .replace(/\\"/g, '"')    // Eliminar escapes de comillas internas
                .replace(/(\r\n|\n|\r)/gm, '')
                .trim();
            
            const finalJson = JSON.parse(finalCleanedContent);
            extractedText = finalJson.response_text;
        } catch (e2) {
            // Si incluso el parseo final falla, devolvemos el contenido original y lo registramos.
            console.error("Fallo de JSON.parse definitivo. Devolviendo texto crudo.", e2);
            return msg.content; 
        }
    }

    // --- Devolver resultado ---
    if (extractedText) {
        // Asegúrate de que los escapes de salto de línea (\n) se muestren como saltos de línea reales.
        return extractedText.replace(/\\n/g, '\n');
    }
    
    // Fallback final
    return msg.content;
};
// FIN DE LA FUNCIÓN CLAVE


export default function Home() {
    const { user, token } = useContext(AuthContext); 
    const { sessionId } = useParams(); 
    
    const [isOpen, setIsOpen] = useState(false);
    const toggleBar = () => setIsOpen(!isOpen);

    // --- ESTADOS CLAVE PARA LA CONVERSACIÓN ---
    const [prompt, setPrompt] = useState('');
    const [currentChatId, setCurrentChatId] = useState(sessionId || null); 
    const [messages, setMessages] = useState([]); 
    
    const initialWelcomeText = token ? `¡Bienvenido! ${user?.username}` : '¡Hola! Bienvenido a DeepCrawler';
    const [welcomeText, setWelcomeText] = useState(initialWelcomeText); 
    
    const [loading, setLoading] = useState(true); 
    const [error, setError] = useState(null);

    const messagesEndRef = useRef(null);
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);


    // 1. LÓGICA DE CARGA INICIAL DE LA SESIÓN 
    useEffect(() => {
        setLoading(!!sessionId); 

        if (sessionId) {
            const fetchSession = async () => {
                setError(null);
                try {
                    const url = `http://localhost:3000/api/chats/${sessionId}`;
                    const res = await fetch(url);

                    if (!res.ok) {
                        const errorData = await res.text(); 
                        if (errorData.startsWith('<!DOCTYPE')) {
                            throw new Error(`Error ${res.status}: La ruta API '${url}' no está activa o devolvió HTML. Verifica el backend.`);
                        }
                        
                        let errorDetails = errorData;
                        try {
                            errorDetails = JSON.parse(errorData).error || errorData; 
                        } catch (e) {}
                        
                        throw new Error(`Fallo al cargar la conversación (Estado ${res.status}): ${errorDetails}`);
                    }
                    
                    const data = await res.json(); 
                    setCurrentChatId(data.sessionId);
                    setMessages(data.messages);
                    setWelcomeText(data.sessionTitle); 
                } catch (err) {
                    console.error("Error loading chat session:", err);
                    setError(err.message);
                    setMessages([]);
                    setCurrentChatId(null);
                    setWelcomeText(initialWelcomeText);
                } finally {
                    setLoading(false);
                }
            };
            fetchSession();
        } else {
            setLoading(false);
            setMessages([]);
            setCurrentChatId(null);
            setWelcomeText(initialWelcomeText);
        }
    }, [sessionId, user]);


    // 2. LÓGICA DE SUBMIT PARA CREAR/CONTINUAR CHAT
    async function handleSubmit(e) {
        e.preventDefault();
        const trimmedPrompt = prompt.trim();
        if (!trimmedPrompt || loading || !user?.email) return;

        const userMessage = { id: Date.now(), content: trimmedPrompt, role: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setPrompt(''); 
        setWelcomeText(`Buscando: ${trimmedPrompt}...`);
        
        setLoading(true);
        setError(null);
        const url = 'http://localhost:3000/api/chats'; 

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    prompt: trimmedPrompt, 
                    sessionId: currentChatId, 
                    userEmail: user.email 
                })
            });
            
            if (!res.ok) {
                 const errorData = await res.text(); 
                 let errorDetails = errorData;
                 
                 if (errorData.startsWith('<!DOCTYPE')) {
                    throw new Error(`Error ${res.status}: El backend devolvió HTML. Verifica el servidor.`);
                 }
                
                 try {
                     errorDetails = JSON.parse(errorData).error || errorData; 
                 } catch (e) {}
                 
                 setError(errorDetails);
                 setMessages(prev => prev.slice(0, -1)); 
                 setWelcomeText(currentChatId ? welcomeText : initialWelcomeText);
                 setLoading(false);
                 return;
            }
            
            const data = await res.json();
            
            if (data.sessionId && data.sessionId !== currentChatId) {
                setCurrentChatId(data.sessionId);
            }
            
            setMessages(data.messages || []); 
            
            setWelcomeText(data.sessionTitle || data.messages[data.messages.length - 1]?.content.substring(0, 50) + '...');
            
        } catch (err) {
            setError(String(err));
            setMessages(prev => prev.slice(0, -1)); 
            setWelcomeText(currentChatId ? welcomeText : initialWelcomeText);
        }
        setLoading(false);
    }

    const isChatting = messages.length > 0;
    const initialWelcomeScreen = !isChatting;

    return (
        <>
            <Aside isOpen={isOpen} toggleBar={toggleBar} />

            <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
                <div className="header">
                    <h1> DeepCrawler </h1>
                </div>
                
                <div className="question-body">
                    {/* Contenido principal: Bienvenida o Historial de Chat */}
                    {initialWelcomeScreen ? (
                        <h1 className="welcome-title">
                            {loading ? "Cargando..." : welcomeText}
                        </h1>
                    ) : (
                        <div className="response-area">
                            {/* 🎯 DIV ADICIONAL SOLICITADO AQUÍ 🎯 */}
                            <div className="chat-messages-scroll-wrapper"> 
                                {messages.map((msg, index) => (
                                    <div key={index} className={`message-container ${msg.role}`}>
                                        <p className="message-content">
                                            {/* 🚨 AQUÍ SE USA LA FUNCIÓN DE EXTRACCIÓN 🚨 */}
                                            {getMessageContent(msg)}
                                        </p>
                                    </div>
                                ))}
                            </div> 
                            {/* 🎯 FIN DEL DIV ADICIONAL 🎯 */}
                            
                            {loading && <p className="loading-message">Buscando...</p>}
                            <div ref={messagesEndRef} />
                        </div>
                    )}
                    
                    {error && <p className="error">Error: {error}</p>}
                    
                    {/* El formulario de entrada siempre está abajo */}
                    <form className="input" onSubmit={handleSubmit}>
                        <input 
                            placeholder="Pregunta a DeepCrawler" 
                            value={prompt} 
                            onChange={(e) => setPrompt(e.target.value)} 
                            disabled={loading || !user}
                        />
                        <div className="tools-kit">
                            <button type="button" className="button-with-text" onClick={() => { /* placeholder */ }} disabled={loading}>
                                <img src={toolsKit} alt="Herramientas"/>
                                <p>Ver mas herramientas</p> 
                            </button>
                            <button type="submit" className="button-without-text" disabled={loading || !prompt.trim()}>
                                <img src={paperPlane} alt="Enviar mensaje"/>
                            </button>
                        </div>
                    </form>

                </div>
            </main>
        </>
    );
}