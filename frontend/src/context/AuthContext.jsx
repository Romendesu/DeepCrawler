import { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export function AuthProvider({children}) {
    // Configuramos los estados 
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);

    // Siempre que entremos, cargamos el token
    useEffect(() => {
        const savedToken = localStorage.getItem("token");
        const savedUser = localStorage.getItem("user");
        // En caso de encontrar la información en localstorage, la añadimos
        if (savedToken) setToken(savedToken);
        if (savedUser) setUser(JSON.parse(savedUser));
    }, []);

    // Al hacer login, almacenamos la informacion
    const login = (userData, tokenValue) => {
        setUser(userData);
        setToken(tokenValue);
        localStorage.setItem("token", tokenValue);
        localStorage.setItem("user",JSON.stringify(userData));
    };

    // Al cerrar sesion, borramos la informacion
    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    };

    return (
        <AuthContext.Provider value={{user, token, login, logout}} >
            {children}
        </AuthContext.Provider>
    )
}