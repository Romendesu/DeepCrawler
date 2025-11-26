import {Chat} from "/src/assets/icons/chatBar/exportIcons"
import styles from "/src/styles/components/chatbar.module.css"

export default function ChatBar ({context, lastChat,creationDate}) {
  return (
    <div className = {styles.container}>
      <img src={Chat} className={styles.img} alt="Historial de mensajes" />
      <div className={styles.textcontainer}>
        <h1> {context} </h1>
        <p> {lastChat} </p>
      </div>
      <p> {creationDate}</p>
    </div>
  )
}
