import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    FlaskConical,
    Code2,
    Activity,
    Shield,
    Zap,
} from 'lucide-react';

export default function Layout({ children }) {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Attack Lab', icon: <Zap size={16} /> },
        { path: '/benchmark', label: 'Benchmark', icon: <Activity size={16} /> },
        { path: '/sandbox', label: 'Code Sandbox', icon: <Code2 size={16} /> },
    ];

    return (
        <div className="app-layout">
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="sidebar-logo-icon">
                            <Shield size={20} color="#fff" />
                        </div>
                        <div>
                            <div className="sidebar-logo-text">AML Visualizer</div>
                            <div className="sidebar-logo-sub">Research Platform</div>
                        </div>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <div className="nav-section-title">Workspace</div>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `nav-item ${isActive ? 'active' : ''}`
                            }
                        >
                            {item.icon}
                            {item.label}
                        </NavLink>
                    ))}

                    <div className="nav-section-title" style={{ marginTop: '24px' }}>
                        Built-in Attacks
                    </div>
                    {['FGSM', 'PGD', 'C&W', 'DeepFool', 'Square'].map((name) => (
                        <div key={name} className="nav-item" style={{ paddingLeft: 20, fontSize: 12, color: 'var(--text-muted)' }}>
                            <FlaskConical size={13} />
                            {name}
                        </div>
                    ))}
                </nav>

                <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                        Adversarial Robustness Toolbox
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
                        v1.18.0 • PyTorch Backend
                    </div>
                </div>
            </aside>

            <main className="main-content">
                {children}
            </main>
        </div>
    );
}
