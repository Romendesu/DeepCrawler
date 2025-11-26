import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/Home";
import Auth from "../pages/Auth";
import NotFound from "../pages/NotFound";
import ConversationRecord from "../pages/ConversationRecord";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/auth", element: <Auth /> },
  { path: "*", element: <NotFound /> },
  { path: "/record", element: <ConversationRecord />}
]);

export default router;
