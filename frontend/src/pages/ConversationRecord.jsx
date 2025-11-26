import Aside from "../components/aside.jsx";
import ChatBar from "../components/chatbar.jsx"; 
import {useState} from "react";


export default function ConversationRecord () {
  const [isOpen, setIsOpen] = useState(false);
  const toggleBar = () => setIsOpen(!isOpen);

  return (
    <>
      <Aside isOpen={isOpen} toggleBar={toggleBar} />
      <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
        <div className="header">
          <h1> DeepCrawler </h1>
        </div>
        <ChatBar context="Titulo" lastChat="lastChat" creationDate="2/11/2025"/>
      </main>
    </>
  )
}

