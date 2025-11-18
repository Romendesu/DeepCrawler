import { createBrowserRouter } from "react-router-dom";
import Home from "../pages/Home";
import Auth from "../pages/Auth";
import NotFound from "../pages/NotFound";

const router = createBrowserRouter([
  { path: "/", element: <Home /> },
  { path: "/auth", element: <Auth /> },
  { path: "*", element: <NotFound /> },
]);

export default router;
