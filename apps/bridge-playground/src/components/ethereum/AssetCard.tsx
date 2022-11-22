import React from 'react';
import { Card, Grid, Typography, CardContent, DialogActions, TextField, Divider } from '@mui/material';

import abi from './abi';
import EthereumSDK from 'src/services/ethereum';
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
    const [modalOpen, setModalOpen] = React.useState<string>();
    const [target, setTarget] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();

    const performAction = React.useCallback(() => {
        const contract = new EthereumSDK.eth.Contract(abi.asset, asset.address);

        if (!modalOpen) {
            return setError(new Error('Invalid action!'));
        }
        if (!target || target.length < 32) {
            return setError(new Error('Invalid address!'));
        }
        if (!amount || amount == '0') {
            return setError(new Error('Invalid amount!'));
        }

        EthereumSDK.eth
            .getAccounts()
            .then(async (accounts) => {
                return contract.methods[modalOpen](target, amount)
                    .send({ from: accounts[0] })
                    .on('transactionHash', function (hash: string) {
                        setOperationHash(hash);
                    });
            })
            .then(console.log)
            .catch(setError);
    }, [asset.address, modalOpen, target, amount]);

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
                            <Typography color="text.secondary">Asset</Typography>
                            <Typography variant="caption" fontSize={10}>
                                <a
                                    target="_blank"
                                    style={{ color: 'white' }}
                                    href={`${Constants.etherscan}/address/${asset.address}`}
                                    rel="noreferrer"
                                >
                                    {asset.address}
                                </a>
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Grid container direction="row" justifyContent="flex-end" alignItems="center" spacing={2}>
                                <Grid item>
                                    <Button fullWidth size="small" onClick={() => setModalOpen('mint')}>
                                        Mint
                                    </Button>
                                </Grid>
                                <Grid item>
                                    <Button fullWidth size="small" onClick={() => setModalOpen('approve')}>
                                        Approve
                                    </Button>
                                </Grid>
                                <Grid item>
                                    <Button fullWidth size="small" onClick={() => setModalOpen('transfer')}>
                                        Trasfer
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
                title={modalOpen?.toUpperCase()}
                open={!!modalOpen}
                onClose={() => {
                    setModalOpen(undefined);
                    setTarget(undefined);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={() => performAction()}>
                            {modalOpen?.toUpperCase()}
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
                    href={`${Constants.etherscan}/tx/${operationHash}`}
                    rel="noreferrer"
                >
                    Etherscan
                </a>
            </Dialog>
        </>
    );
};

export default AssetCard;
