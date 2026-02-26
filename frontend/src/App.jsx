import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Benchmark from './pages/Benchmark';
import Sandbox from './pages/Sandbox';

export default function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/benchmark" element={<Benchmark />} />
                    <Route path="/sandbox" element={<Sandbox />} />
                </Routes>
            </Layout>
        </Router>
    );
}
