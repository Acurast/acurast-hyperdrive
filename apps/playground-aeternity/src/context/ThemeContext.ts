import { createContext } from 'react';

export enum ThemeKind {
    Dark = 'dark',
    Light = 'light',
}

export interface IThemeContext {
    theme: ThemeKind;
    setTheme: (t: ThemeKind) => void;
}

const contextStub = {
    theme: ThemeKind.Dark,
    setTheme: () => {
        // stub
    },
};

const ThemeContext = createContext<IThemeContext>(contextStub);

export default ThemeContext;
