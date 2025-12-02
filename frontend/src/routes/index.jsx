import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/Home";
import Auth from "../pages/Auth";
import NotFound from "../pages/NotFound";
import Config from "../pages/Config"
import ConversationRecord from "../pages/ConversationRecord";

const router = createBrowserRouter([
    // 1. Ruta principal para iniciar un NUEVO chat (Sin ID)
    { path: "/", element: <Home /> }, 
    
    // 2. Nueva ruta para CARGAR un chat existente (Con ID)
    // El parámetro :sessionId será leído por el hook useParams() en Home.jsx
    { path: "/chat/:sessionId", element: <Home /> }, 

    { path: "/auth", element: <Auth /> },
    { path: "/config", element: <Config /> },
    
    // 3. Ruta para el historial de conversaciones
    { path: "/record", element: <ConversationRecord />},
    
    // 4. Catch-all para rutas no encontradas
    { path: "*", element: <NotFound /> },
]);

export default router;