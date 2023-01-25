import React from 'react';
import { Container, Grid, Typography } from '@mui/material';
import TezosCrowdfunding from 'src/components/tezos/crowdfunding';
import EthereumCrowdfunding from 'src/components/ethereum/crowdfunding';

const Crowdfund: React.FC = () => {
    return (
        <Container>
            <Typography variant="overline">Crowdfund</Typography>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginBottom: 10 }}
            >
                <Grid item xs={6}>
                    <TezosCrowdfunding />
                </Grid>
                <Grid item xs={6}>
                    <EthereumCrowdfunding />
                </Grid>
            </Grid>
        </Container>
    );
};
export default Crowdfund;
