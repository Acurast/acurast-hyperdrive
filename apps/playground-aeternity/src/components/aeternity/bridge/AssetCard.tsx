import React from 'react';
import { Card, Grid, Typography, CardContent, Divider } from '@mui/material';

import { AssetInfo } from 'src/context/AppContext';
import Constants from 'src/constants';

interface OwnProps {
    asset: AssetInfo;
}

const AssetCard: React.FC<OwnProps> = ({ asset }) => {
    return (
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
                                href={`${Constants.aeternity.explorer}/contracts/${asset.address}`}
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
    );
};

export default AssetCard;
