import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

const ThemeProvider = ({ children }) => {
    const storedTheme = localStorage.getItem('theme');
    const [theme, setTheme] = useState(storedTheme || 'light');

    useEffect(() => {
        // Apply the theme to the HTML element
        document.documentElement.setAttribute('data-theme', theme);
        // Save the theme to localStorage
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export default ThemeProvider;
