import React from 'react';
import { Card, Grid, Typography, CardContent, DialogActions, TextField, Divider } from '@mui/material';

import Button from 'src/components/base/Button';
import Dialog from '../base/Dialog';
import { AssetInfo } from 'src/context/AppContext';
import Constants from 'src/constants';

interface OwnProps {
    asset: AssetInfo;
}

const AssetCard: React.FC<OwnProps> = ({ asset }) => {
    const [operationHash, setOperationHash] = React.useState('');
    const [error, setError] = React.useState<Error>();
    const [approveModalOpen, setApproveModalOpen] = React.useState(false);
    const [target, setTarget] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();

    const approve = React.useCallback(() => null, [asset.address, target, amount]);

    const handleTarget = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setTarget(e.target.value);
    }, []);

    const handleAmount = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setAmount(e.target.value);
    }, []);

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
                        <Grid item>
                            <Grid container direction="row" justifyContent="flex-end" alignItems="center" spacing={2}>
                                <Grid item>
                                    <Button fullWidth size="small" onClick={() => setApproveModalOpen(true)}>
                                        Approve
                                    </Button>
                                </Grid>
                            </Grid>
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

            <Dialog
                title="Approve token"
                open={approveModalOpen}
                onClose={() => {
                    setApproveModalOpen(false);
                    setTarget(undefined);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={approve}>
                            Approve
                        </Button>
                    </DialogActions>
                }
            >
                <TextField
                    error={!target}
                    placeholder="Address (0x...)"
                    onChange={handleTarget}
                    fullWidth
                    margin="dense"
                />
                <TextField error={!amount} placeholder="Amount" onChange={handleAmount} fullWidth margin="dense" />
            </Dialog>

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
