/*const cors = require('cors')
const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const { MongoClient } = require('mongodb');
const dotenv = require('dotenv');*/
import cors from 'cors';
import express from 'express';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';

dotenv.config();
const app=express();
app.use(express.json());
app.use(cors())
const PORT = process.env.PORT || 9000;
app.listen(PORT, () => {
  console.log('Server Listening on PORT:', PORT);
});

const MONGODB_URI = process.env.MONGODB_URI;
const client = new MongoClient(MONGODB_URI);
let db;
await client.connect();
db = client.db('Apollo');

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const getCourseData = async () => {
  const courses = await db.collection('Catalog').find({}).toArray(); // Replace 'courses' with your collection name

  // Format each course into a readable string
   const courseDescriptions =  courses.map(course => {
    // Build the course description dynamically
    let courseInfo = `Course or Course Code: ${course.Code || "None"}. Credits: ${course.Credits || "None"}, Hours: ${course.Hours || "None"}.`;
    courseInfo += ` Description: ${course.Description || "None"}.`;

    // Add prerequisites if available
    if (course.Prerequisites) {
      courseInfo += ` Prerequisites: ${course.Prerequisites}.`;
    } else {
      courseInfo += ` Prerequisites: None.`;
    }

    // Add corequisites if available
    if (course.Corequisites) {
      courseInfo += ` Corequisites: ${course.Corequisites}.`;
    } else {
      courseInfo += ` Corequisites: None.`;
    }

    // Add prerequisites or corequisites if available
    if (course["Prerequisites or Corequisites"]) {
      courseInfo += ` Prerequisites or Corequisites: ${course["Prerequisites or Corequisites"]}.`;
    } else {
      courseInfo += ` Prerequisites or Corequisites: None.`;
    }

    return courseInfo;
  });

  return courseDescriptions.join("\n\n");
  
};

app.post("/chat", async (req, res) => {
    const chatHistory = req.body.history || [];
    const msg = req.body.chat;
    
    const courseData = await getCourseData();

    const chat = model.startChat({
      history: [
        {
          role: "user",
          parts: [{text: "You are an AI assistant for a university course catalog. Answer questions based on the provided course data." }]
        },
        {
          role: "user",
          parts: [{text: courseData}]
        },
        {
          role: "user",
          parts: [{text: msg}]
        },
        ...chatHistory
      ]
    });

    const result = await chat.sendMessage(msg);
    const response = await result.response;
    const text = response.text();
    res.send({"text":text});
  });

app.post("/stream", async (req, res) => {
    let chatHistory = req.body.history || [];
    const msg = req.body.chat;

    const courseData = await getCourseData();

    const chat = model.startChat({
      history: [
        {
          role: "user",
          parts: [{text: "You are an AI assistant for a university course catalog. Answer questions based on the provided course data." }]
        },
        {
          role: "user",
          parts: [{text: courseData}]
        },
        {
          role: "user",
          parts: [{text: msg}]
        },
        ...chatHistory
      ]
    });

    const result = await chat.sendMessageStream(msg);
    for await (const chunk of result.stream) {
      const chunkText = chunk.text();
      res.write(chunkText);
    }
    res.end();
  });
