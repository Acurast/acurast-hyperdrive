import React from 'react';
import { Container, Grid, Typography } from '@mui/material';
import TezosBridge from 'src/components/aeternity/bridge';
import EthereumBridge from 'src/components/ethereum/bridge';

const Bridge: React.FC = () => {
    return (
        <Container>
            <Typography variant="overline">Bridge</Typography>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginBottom: 10 }}
            >
                <Grid item xs={6}>
                    <TezosBridge />
                </Grid>
                <Grid item xs={6}>
                    <EthereumBridge />
                </Grid>
            </Grid>
        </Container>
    );
};
export default Bridge;
