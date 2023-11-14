import React from 'react';
import ReactDOMClient from 'react-dom/client';

import './index.css';
import reportWebVitals from './reportWebVitals';
import ThemeProvider from './context/ThemeProvider';
import Router from './Routes';
import AppProvider from './context/AppProvider';

const container = document.getElementById('root');
if (!container) {
    alert('Root <div/> missing!');
    throw new Error('Root <div/> missing!');
}

// For some reason Web3 depends on the process api
global.process = require('process');

const App = () => (
    <ThemeProvider>
        <AppProvider>
            <Router />
        </AppProvider>
    </ThemeProvider>
);

ReactDOMClient.createRoot(container).render(<App />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
