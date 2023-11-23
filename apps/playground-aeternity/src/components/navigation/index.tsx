import React from 'react';
import {
    Box,
    Toolbar,
    AppBar,
    Divider,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent,
} from '@mui/material';

import DarkLightSwitch from '../theme/DarkLightSwitch';
import RouterButton from './RouterButton';
import useAppContext from 'src/hooks/useAppContext';
import { Network } from 'src/context/AppContext';

const NavigationBar = () => {
    const { network, updateNetwork } = useAppContext();

    const handleNetworkChange = React.useCallback((evt: SelectChangeEvent<Network>) => {
        updateNetwork(evt.target.value as Network);
    }, []);

    return (
        <AppBar position="static" color="default">
            <Toolbar>
                <Typography>
                    <span style={{ color: 'white' }}>ACURAST</span>
                </Typography>
                <Box sx={{ flexGrow: 1 }} />

                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <DarkLightSwitch />
            </Toolbar>
        </AppBar>
    );
};

export default NavigationBar;
