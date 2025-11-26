import {chat} from "/src/assets/icons/aside/exportIcons"
import styles from "/src/styles/components/chatbar.module.css"

export default function ChatBar ({context, lastChat,creationDate}) {
  return (
    <div className = {styles.container}>
      <img src={chat} alt="Historial de mensajes" />
      <div className="text-container">
        <h1> {context} </h1>
        <p> {lastChat} </p>
      </div>
      <p> {creationDate}</p>
    </div>
  )
}
