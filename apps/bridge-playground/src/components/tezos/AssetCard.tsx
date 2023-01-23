import React from 'react';
import { Card, Grid, Typography, CardContent, Divider, Box } from '@mui/material';

import Dialog from '../base/Dialog';
import { AssetInfo } from 'src/context/AppContext';
import Constants from 'src/constants';

interface OwnProps {
    asset: AssetInfo;
}

const AssetCard: React.FC<OwnProps> = ({ asset }) => {
    const [operationHash, setOperationHash] = React.useState('');
    const [error, setError] = React.useState<Error>();

    return (
        <>
            <Card variant="outlined">
                <CardContent>
                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Asset
                            </Typography>
                            <Typography variant="caption" fontSize={10}>
                                <a
                                    target="_blank"
                                    style={{ color: 'white' }}
                                    href={`${Constants.tzkt}/${asset.address}`}
                                    rel="noreferrer"
                                >
                                    {asset.address}
                                </a>
                            </Typography>
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Balance
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                {asset.balance}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <Dialog title="Error" open={!!error} onClose={() => setError(undefined)}>
                {error?.message || ''}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                <a
                    style={{ color: 'white' }}
                    target="_blank"
                    href={`https://goerli.etherscan.io/tx/${operationHash}`}
                    rel="noreferrer"
                >
                    Etherscan
                </a>
            </Dialog>
        </>
    );
};

export default AssetCard;
