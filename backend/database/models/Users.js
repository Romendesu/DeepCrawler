const { Model, DataTypes } = require("sequelize");
const sequelize = require("../db");

class User extends Model {}

User.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,          
    autoIncrement: true,       
    allowNull: false
  },
  username: { 
    type: DataTypes.STRING, 
    allowNull: false 
  },
  email: { type: DataTypes.STRING, 
    allowNull: false, 
    unique: true 
  },
  password: { 
    type: DataTypes.STRING, 
    allowNull: false },
  image: { 
    type: DataTypes.TEXT 
  }
}, {
  sequelize,
  modelName: 'User',
  tableName: 'users'
});

module.exports = User;
