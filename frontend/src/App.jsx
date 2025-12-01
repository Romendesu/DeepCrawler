import { RouterProvider } from "react-router-dom";
import router from "./routes";
import { PopUpProvider, PopUpContext } from "./context/PopUpContext";
import { AuthProvider } from "./context/AuthContext";
import PopUp from "./components/popup";
import { useContext } from "react";

export default function App() {
  return (
    <AuthProvider>
      <PopUpProvider>
        <AppContent />
      </PopUpProvider>
    </AuthProvider>
  );
}

function AppContent() {
  const { popup } = useContext(PopUpContext);

  return (
    <>
      <RouterProvider router={router} />
      {popup.show && (
        <PopUp
          state={popup.type}
          title={popup.title}
          subtitle={popup.subtitle}
        />
      )}
    </>
  );
}
