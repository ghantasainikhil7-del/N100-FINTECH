import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { BluestockProvider } from './context/useBluestockData.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BluestockProvider>
      <App />
    </BluestockProvider>
  </React.StrictMode>,
);
