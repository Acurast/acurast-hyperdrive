import React from 'react';
import { Box, Toolbar, AppBar, Divider, Typography } from '@mui/material';

import DarkLightSwitch from '../theme/DarkLightSwitch';
import RouterButton from './RouterButton';

const NavigationBar = () => {
    return (
        <AppBar position="static" color="default">
            <Toolbar>
                <Typography>
                    Inter Blockchain Communication Protocol <span style={{ color: 'red' }}>Examples</span>
                </Typography>
                <Box sx={{ flexGrow: 0.6 }} />
                <RouterButton to="/bridge" variant="outlined">
                    Bridge
                </RouterButton>
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <RouterButton to="/crowdfund" variant="outlined">
                    Crowdfund
                </RouterButton>
                <Box sx={{ flexGrow: 1 }} />
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <DarkLightSwitch />
            </Toolbar>
        </AppBar>
    );
};

export default NavigationBar;
