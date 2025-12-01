import { useEffect, useState } from "react";
import styles from "/src/styles/components/popup.module.css";

export default function PopUp({ state, title, subtitle, onClose }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Mostrar el popup (activar transición)
    setVisible(true);

    // Desaparece tras 3s
    const timer = setTimeout(() => {
      setVisible(false);

      // Espera la transición antes de remover del DOM
      setTimeout(onClose, 300);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`${styles.container} ${visible ? styles.show : ""} ${state ? styles[state] : ""}`}>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  );
}
