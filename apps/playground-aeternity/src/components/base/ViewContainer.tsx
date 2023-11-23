import React from 'react';
import { makeStyles } from '@mui/styles';

import NavigationBar from '../navigation';
import Typography from '@mui/material/Typography';

const useStyles = makeStyles({
    root: {
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
    },
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 'calc(10px + 2vmin)',
        flex: 1,
    },
    footer: {
        width: '100%',
        height: 50,
        borderTop: '1px solid #eaeaea',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    },
    link: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        textDecoration: 'none',
        color: 'inherit',
    },
});

const ViewContainer: React.FC<{ children: React.ReactNode }> = (props) => {
    const classes = useStyles();
    return (
        <div className={classes.root}>
            <NavigationBar />
            <div className={classes.container}>{props.children}</div>
            <footer className={classes.footer}>
                <a href="https://acurast.com" target="_blank" rel="noopener noreferrer" className={classes.link}>
                    <Typography variant="overline" style={{ marginRight: '0.5em' }}>
                        Powered by Acurast
                    </Typography>
                </a>
            </footer>
        </div>
    );
};

export default ViewContainer;
