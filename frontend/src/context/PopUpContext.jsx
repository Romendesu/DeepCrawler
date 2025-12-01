// src/contexts/PopUpContext.jsx
import { createContext, useState } from "react";

export const PopUpContext = createContext();

export function PopUpProvider({ children }) {
  const [popup, setPopup] = useState({
    show: false,
    title: "",
    subtitle: "",
    type: "", // 'active' o 'error'
  });

  const showPopUp = ({ title, subtitle, type }) => {
    setPopup({ show: true, title, subtitle, type });
    setTimeout(() => setPopup((prev) => ({ ...prev, show: false })), 3000);
  };

  return (
    <PopUpContext.Provider value={{ popup, showPopUp }}>
      {children}
    </PopUpContext.Provider>
  );
}
