import Aside from "../components/aside.jsx";
import { useState, useContext, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import styles from "../styles/components/config.module.css"

export default function ConversationRecord () {
    const {user, token, logout, setUser} = useContext(AuthContext); 

    const [isOpen, setIsOpen] = useState(false);
    const toggleBar = () => setIsOpen(!isOpen);

    // --- ESTADOS PARA GESTIONAR CAMBIOS ---
    const [newUsername, setNewUsername] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [newProfilePic, setNewProfilePic] = useState(null); // Objeto File
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    // ----------------------------------------

    // Estado para manejar la URL de previsualización temporal (Blob URL)
    const [newProfilePicUrl, setNewProfilePicUrl] = useState(null);

    // Función para decodificar la cadena Base64 y crear una Data URL
    const decodeBase64 = (base64String) => {
        if (!base64String || typeof base64String !== 'string') return null;
        if (base64String.startsWith('data:')) return base64String;
        return `data:image/jpeg;base64,${base64String}`;
    }

    // URL de la imagen existente (del usuario)
    const profileImageUrl = decodeBase64(user?.pfp);
    
    // URL que se muestra (prioriza la nueva URL de previsualización)
    const displayImageUrl = newProfilePicUrl || profileImageUrl;


    // --- GESTIÓN DEL EFECTO DE IMAGEN DE PERFIL ---

    // 1. Crea la URL de previsualización cuando se selecciona un archivo
    useEffect(() => {
        if (newProfilePic) {
            const url = URL.createObjectURL(newProfilePic);
            setNewProfilePicUrl(url);
            
            // 2. Función de limpieza: revoca la URL cuando el componente se desmonta 
            // o cuando newProfilePic cambia a null.
            return () => {
                URL.revokeObjectURL(url);
                setNewProfilePicUrl(null);
            };
        } else {
             // Limpiar la URL de previsualización si el archivo se borra (ej. después de guardar)
            if(newProfilePicUrl) {
                URL.revokeObjectURL(newProfilePicUrl);
                setNewProfilePicUrl(null);
            }
        }
    }, [newProfilePic]); // Se ejecuta cuando el archivo seleccionado cambia


    // --- MANEJADORES DE EVENTOS ---

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file && file.size < 5 * 1024 * 1024) { // Límite de 5MB
            // Antes de establecer el nuevo, limpiamos la URL anterior si existe
            if(newProfilePicUrl) URL.revokeObjectURL(newProfilePicUrl); 
            
            setNewProfilePic(file);
            setError(null);
            e.target.value = null;
        } else if (file) {
            setError('La imagen de perfil debe ser menor de 5MB.');
            e.target.value = null;
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        if (newUsername.trim() !== '') formData.append('username', newUsername.trim());
        if (newEmail.trim() !== '') formData.append('email', newEmail.trim());
        if (newPassword.trim() !== '') formData.append('password', newPassword.trim());
        if (newProfilePic) formData.append('pfp', newProfilePic);

        if (formData.entries().next().done) {
            setError('No has introducido ningún cambio.');
            setLoading(false);
            return;
        }

        try {
            const url = `http://localhost:3000/api/users/${user.id}`; 
            const res = await fetch(url, {
                method: 'PUT',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Fallo al actualizar el perfil.');
            }

            // Clave: Esto actualiza el estado de React. El AuthContext corregido 
            // se encarga de guardarlo en localStorage.
            setUser(data.user); 
            setSuccess('¡Perfil actualizado con éxito!');
            
            // Limpiar los estados para evitar reenvíos accidentales
            setNewUsername('');
            setNewEmail('');
            setNewPassword('');
            
            // Esto dispara el useEffect para revocar la URL y limpiar el estado
            setNewProfilePic(null); 

        } catch (err) {
            console.error('Error al actualizar el perfil:', err);
            setError(err.message || 'Error desconocido al actualizar.');
        } finally {
            setLoading(false);
        }
    };


    return (
        <>
            <Aside isOpen={isOpen} toggleBar={toggleBar} />
            <main className={`main-content ${isOpen ? "aside-abierta" : "aside-cerrada"}`}>
                <div className="header">
                    <h1> DeepCrawler </h1>
                </div>
                
                <form className={styles.mainContainer} onSubmit={handleSubmit} >
                    <h1>Configuración</h1>
                    
                    <div className={styles.profilePictureWrapper}> 
                        {/* Usamos displayImageUrl para mostrar la imagen */}
                        {displayImageUrl ? (
                            <img 
                                src={displayImageUrl} 
                                alt={`${user?.username}'s profile picture`} 
                                style={{ objectFit: 'cover' }} 
                            />
                        ) : (
                            <svg height="100" width="100" viewBox="0 0 24 24" fill="var(--white)" className={styles.defaultUserIcon}>
                                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                            </svg>
                        )}
                        
                        <input 
                            type="file" 
                            id="pfp-upload" 
                            onChange={handleFileChange} 
                            accept="image/*"
                            className={styles.fileInput}
                        />
                        <label htmlFor="pfp-upload" className={styles.uploadButton} disabled={loading}>
                            Cambiar Foto
                        </label>
                    </div>

                    <p><strong>Nombre de usuario actual:</strong> {user?.username}</p>
                    <p><strong>Correo Electrónico actual:</strong> {user?.email}</p>
                    
                    <div className={styles.changeForm}>
                        <input 
                            name="username" 
                            placeholder="Nuevo nombre de usuario" 
                            type="text"
                            value={newUsername}
                            onChange={(e) => setNewUsername(e.target.value)}
                            disabled={loading}
                        />
                        <input 
                            name="email" 
                            placeholder="Nuevo correo electrónico" 
                            type="email"
                            value={newEmail}
                            onChange={(e) => setNewEmail(e.target.value)}
                            disabled={loading}
                        />
                        <input 
                            name="password" 
                            placeholder="Nueva contraseña" 
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    
                    {error && <p className={styles.errorMessage}>{error}</p>}
                    {success && <p className={styles.successMessage}>{success}</p>}

                    <button type="submit" className={styles.submitButton} disabled={loading || !user}>
                        {loading ? 'Guardando...' : 'Guardar Cambios'}
                    </button>
                    
                </form>
            </main>
        </>
    )
}