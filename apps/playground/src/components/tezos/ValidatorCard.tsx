import React from 'react';
import { Card, Grid, Typography, CardContent, Divider } from '@mui/material';

import useAppContext from 'src/hooks/useAppContext';
import Constants from 'src/constants';

const ValidatorCard: React.FC = () => {
    const { tezos } = useAppContext();

    return (
        <>
            <Card variant="outlined">
                <CardContent>
                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Validator
                            </Typography>
                            <Typography variant="caption" fontSize={10}>
                                <a
                                    target="_blank"
                                    style={{ color: 'white' }}
                                    href={`${Constants.tzkt}/${Constants.evm_validator}`}
                                    rel="noreferrer"
                                >
                                    {Constants.evm_validator}
                                </a>
                            </Typography>
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Grid container direction="column" justifyContent="space-between" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                Latest Snapshot
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Typography variant="caption">
                                {tezos.validatorInfo?.latestSnapshot.block_number}
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Typography variant="caption">{tezos.validatorInfo?.latestSnapshot.merkle_root}</Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </>
    );
};

export default ValidatorCard;
