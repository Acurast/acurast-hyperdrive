import React from 'react';
import { Container, Grid } from '@mui/material';
import Tezos from 'src/components/tezos/Card';
import Ethereum from 'src/components/ethereum/Card';

const Home: React.FC = () => {
    return (
        <Container>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginTop: 10, marginBottom: 10 }}
            >
                <Grid item xs={6}>
                    <Tezos />
                </Grid>
                <Grid item xs={6}>
                    <Ethereum />
                </Grid>
            </Grid>
        </Container>
    );
};
export default Home;
