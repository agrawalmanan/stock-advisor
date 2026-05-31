import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDnKBYa0yFv9P_9vOf64P8E-ubFWtTL9gI",
  authDomain: "stock-advisor-7ca3b.firebaseapp.com",
  projectId: "stock-advisor-7ca3b",
  storageBucket: "stock-advisor-7ca3b.firebasestorage.app",
  messagingSenderId: "833081877996",
  appId: "1:833081877996:web:391e28c4a027a08605ccc9"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const db = getFirestore(app);

export default app;