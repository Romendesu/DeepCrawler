const express = require('express');
const syncDB = require('./database/sync');
const cors = require("cors");
const authRoutes = require('./routes/auth');

// Middlewares
const app = express();
app.use(express.json());
app.use(cors({
  origin: "http://localhost:5173",
  methods: ["GET", "POST", "PUT", "DELETE"],
  credentials: true
}));

// Rutas
app.use('/auth', authRoutes);

syncDB().then(() => {
  app.listen(3000, () => console.log('Servidor corriendo en http://localhost:3000'));
});
