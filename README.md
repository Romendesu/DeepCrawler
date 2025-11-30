# DeepCrawler

## 1. ¿Qué es DeepCrawler?

DeepCrawler es un webcrawler que emplea agentes de IA para buscar información por internet. Su interfaz es muy similar a las que proporcionan Gemini, ChatGPT y otros asistentes conversacionales, permitiendo a los usuarios interactuar de manera sencilla y eficiente con la información que buscan.

Es una aplicación web que cuenta con las siguientes tecnologías:

  1. Front-end: React + Vite, empleando CSS Vanilla
  2. Back-end: Express + SQLite3, para el manejo de peticiones

## 2. Requerimientos

Para ejecutar DeepCrawler, necesitas tener instalados:

- Node.js (versión recomendada 18+)
- npm (Node Package Manager)

Opcionalmente, para manejar la base de datos local:

- SQLite (incluido en las dependencias de Node)
- Navegador moderno para la interfaz React

## 3. Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/deepcrawler.git
cd deepcrawler
```

2. Instala las dependencias (Tanto en backend, como en frontend):
```bash
npm install
```
3. En una terminal, ejecuta la siguiente secuencia de comandos para inicializar el frontend:
```bash
cd frontend
npm run dev
```
4. En otra terminal, ejecuta la siguiente información para inicializar el backend
```bash
cd backend
node server.js
```


