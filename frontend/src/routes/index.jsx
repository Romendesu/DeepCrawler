import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/Home";
import Auth from "../pages/Auth";
import NotFound from "../pages/NotFound";
import Config from "../pages/Config"
import ConversationRecord from "../pages/ConversationRecord";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/auth", element: <Auth /> },
  { path: "/config", element: <Config /> },
  { path: "*", element: <NotFound /> },
  { path: "/record", element: <ConversationRecord />}
]);

export default router;
