const express = require('express');
const connectDB = require('./db');
const mongoose = require('mongoose');

const app = express();

// Connect to MongoDB
connectDB();

app.use(express.json());

app.listen(process.env.PORT, () => console.log('Server running on port ', process.env.PORT));

// Use the 'apollo' database
const apolloDB = mongoose.connection.useDb('Apollo');

// Define the User model for the 'apollo' database
const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  age: { type: Number, required: true },
});

const User = apolloDB.model('User', userSchema); // Use apolloDB connection for the User model

// Example: Add a new user
const addUser = async () => {
  try {
    const newUser = new User({
      name: 'John Doe',
      email: 'johndoe@example.com',
      age: 30,
    });

    await newUser.save();
    console.log('User added successfully:', newUser);
  } catch (error) {
    console.error('Error adding user:', error);
  }
};

addUser();