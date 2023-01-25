import React from 'react';

import { makeStyles, createStyles } from '@mui/styles';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Light from '@mui/icons-material/Brightness7';
import Dark from '@mui/icons-material/Brightness4';
import useThemeContext from '../../hooks/useThemeContext';
import { ThemeKind } from '../../context/ThemeContext';

const useStyles = makeStyles(() =>
    createStyles({
        themeToggle: {
            width: 48,
            height: 48,
        },
    }),
);

const DarkLightSwitch: React.FC = () => {
    const { theme, setTheme } = useThemeContext();
    const classes = useStyles();

    return (
        <Tooltip
            title={`Toggle ${theme === ThemeKind.Dark ? ThemeKind.Dark : ThemeKind.Light} theme`}
            aria-label="theme"
            placement="left"
            className={classes.themeToggle}
        >
            <IconButton
                aria-label="theme"
                size="small"
                onClick={() => setTheme(theme === ThemeKind.Dark ? ThemeKind.Light : ThemeKind.Dark)}
            >
                {theme === ThemeKind.Dark ? <Dark /> : <Light />}
            </IconButton>
        </Tooltip>
    );
};

export default DarkLightSwitch;
