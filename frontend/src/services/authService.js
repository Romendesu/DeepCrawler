// Llamadas al back-end

export async function signup(username, email, password, confirmPassword) {
    const res = await fetch("http://localhost:3000/auth/sing-up", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username,email,password,confirmPassword})
    })
    return await res.json();
}

export async function login(email, password) {
    const res = await fetch("http://localhost:3000/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    })
    return await res.json();
}