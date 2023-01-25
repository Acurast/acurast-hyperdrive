import { useContext } from 'react';

import ThemeContext, { IThemeContext } from '../context/ThemeContext';

function useThemeContext(): IThemeContext {
    const context = useContext<IThemeContext>(ThemeContext);
    if (context == null) {
        throw new Error('`useThemeContext` not available.');
    }
    return context;
}

export default useThemeContext;
