import { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export function AuthProvider({children}) {
    // Configuramos los estados 
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);

    // 1. Efecto Inicial: Cargar desde localStorage
    useEffect(() => {
        const savedToken = localStorage.getItem("token");
        const savedUser = localStorage.getItem("user");
        
        // En caso de encontrar la información en localstorage, la añadimos
        if (savedToken) setToken(savedToken);
        if (savedUser) setUser(JSON.parse(savedUser));
    }, []);

    // 2. Efecto de Sincronización: Guarda el usuario actualizado en localStorage.
    // ESTO ES LA CLAVE para que los cambios de Configuración se guarden.
    useEffect(() => {
        if (user) {
            // Este efecto se dispara cada vez que setUser actualiza el estado 'user'.
            localStorage.setItem("user", JSON.stringify(user));
        }
    }, [user]); 

    // Al hacer login, almacenamos la informacion
    const login = (userData, tokenValue) => {
        // setUser se encargará de guardar 'user' en localStorage gracias al useEffect anterior.
        setUser(userData);
        setToken(tokenValue);
        localStorage.setItem("token", tokenValue);
    };

    // Al cerrar sesion, borramos la informacion
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    };

    return (
        <AuthContext.Provider value={{user, token, login, logout, setUser, setToken}} >
            {children}
        </AuthContext.Provider>
    )
}