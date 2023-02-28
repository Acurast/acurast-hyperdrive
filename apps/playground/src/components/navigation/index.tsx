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
                <FormControl size="small">
                    <InputLabel id="network-selection-label">Network</InputLabel>
                    <Select
                        labelId="network-selection"
                        id="network-selection"
                        value={network}
                        label="Network"
                        onChange={handleNetworkChange}
                    >
                        <MenuItem value={Network.Ethereum}>Goerli</MenuItem>
                        <MenuItem value={Network.Polygon}>Polygon</MenuItem>
                        <MenuItem value={Network.BSC}>Bsc</MenuItem>
                    </Select>
                </FormControl>
                <Divider flexItem orientation="vertical" sx={{ margin: 1 }} />
                <DarkLightSwitch />
            </Toolbar>
        </AppBar>
    );
};

export default NavigationBar;
