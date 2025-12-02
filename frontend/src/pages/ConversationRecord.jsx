import Aside from "../components/aside.jsx";
import ChatBar from "../components/chatbar.jsx"; 
import {useState, useEffect, useContext} from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from 'react-router-dom';

export default function ConversationRecord () {
    const [isOpen, setIsOpen] = useState(false);
    const toggleBar = () => setIsOpen(!isOpen);
    
    // Estado para almacenar el historial de chats
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const { user } = useContext(AuthContext); 
    const navigate = useNavigate(); // Hook para la navegación

    // Función que maneja el clic en la barra de chat y navega a la vista Home
    const handleChatSelect = (sessionId) => {
        navigate(`/chat/${sessionId}`); 
    };

    // Función para cargar el historial de chats al montar el componente
    useEffect(() => {
        // Asegurarse de que el usuario y el email estén disponibles
        if (!user || !user.email) {
            setError("Usuario no autenticado o email no disponible.");
            setLoading(false);
            return;
        }

        const fetchHistory = async () => {
            setLoading(true);
            setError(null);
            try {
                // Llama a la ruta GET /api/chats/history?email=...
                const res = await fetch(`http://localhost:3000/api/chats/history?email=${user.email}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                });
                
                const data = await res.json();
                
                if (!res.ok) {
                    throw new Error(data.error || 'Fallo al cargar el historial.');
                }

                setChatHistory(data); 

            } catch (err) {
                console.error("Error fetching chat history:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [user]); // Se ejecuta cuando el componente se monta y el 'user' está disponible

    // --- Lógica de Renderizado ---
    
    if (loading) {
        return (
            <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
                <div className="header"><h1>DeepCrawler</h1></div>
                <p>Cargando historial de conversaciones...</p>
            </main>
        );
    }

    if (error) {
        return (
            <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
                <div className="header"><h1>DeepCrawler</h1></div>
                <p className="error">Error al cargar: {error}</p>
            </main>
        );
    }
    
    return (
        <>
            <Aside isOpen={isOpen} toggleBar={toggleBar} />
            <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
                <div className="header">
                    <h1> DeepCrawler </h1>
                </div>
                
                {chatHistory.length === 0 ? (
                    <p>No tienes conversaciones anteriores.</p>
                ) : (
                    // Mapeo dinámico de los chats
                    chatHistory.map((chat) => (
                        <div 
                            key={chat.id} 
                            onClick={() => handleChatSelect(chat.id)} // 👈 Llama a la función de navegación
                            // Usa un estilo o clase para indicar que es clickable
                            style={{ cursor: 'pointer' }} 
                        >
                            <ChatBar 
                                context={chat.title} // Título de la sesión (prompt inicial)
                                lastChat={chat.lastMessageContent || "Sin mensajes recientes"} 
                                creationDate={new Date(chat.createdAt).toLocaleDateString()}
                            />
                        </div>
                    ))
                )}

            </main>
        </>
    )
}