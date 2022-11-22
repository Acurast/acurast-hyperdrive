import React from 'react';
import { Box, Toolbar, AppBar, Divider, Typography } from '@mui/material';

import DarkLightSwitch from '../theme/DarkLightSwitch';

const NavigationBar = () => {
    return (
        <AppBar position="static" color="default">
            <Toolbar>
                <Box sx={{ flexGrow: 1 }} />
                <Typography>
                    Inter Blockchain Communication Protocol <span style={{ color: 'red' }}>Proof of Concept</span>
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <DarkLightSwitch />
            </Toolbar>
        </AppBar>
    );
};

export default NavigationBar;
