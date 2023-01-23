import React from 'react';
import { Box, Toolbar, AppBar, Divider, Typography } from '@mui/material';

import DarkLightSwitch from '../theme/DarkLightSwitch';
import Button from '../base/Button';

const NavigationBar = () => {
    return (
        <AppBar position="static" color="default">
            <Toolbar>
                <Typography>
                    Inter Blockchain Communication Protocol <span style={{ color: 'red' }}>Examples</span>
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Button>Bridge</Button>
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <Button>Swap</Button>
                <Box sx={{ flexGrow: 1 }} />
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <DarkLightSwitch />
            </Toolbar>
        </AppBar>
    );
};

export default NavigationBar;
