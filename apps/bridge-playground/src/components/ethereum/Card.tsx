import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, TextField, DialogActions } from '@mui/material';
import * as IbcfSdk from 'ibcf-sdk';

import abi from './abi';
import EthereumSDK, { Contract } from 'src/services/ethereum';
import Button from 'src/components/base/Button';
import EthereumIcon from 'src/components/base/icons/ethereum';
import useAppContext from 'src/hooks/useAppContext';
import WrapsTable from './Table';
import Constants from 'src/constants';
import Dialog from '../base/Dialog';
import AssetCard from './AssetCard';
import Logger from 'src/services/logger';

const Ethereum = () => {
    const { ethereum } = useAppContext();
    const [operationHash, setOperationHash] = React.useState('');
    const [error, setError] = React.useState<Error>();
    const [wrapModalOpen, setWrapModalOpen] = React.useState(false);
    const [destination, setDestination] = React.useState<string>();
    const [amount, setAmount] = React.useState<string>();
    const [confirming, setConfirming] = React.useState(false);

    const wrap = React.useCallback(async () => {
        const contract = new Contract(Constants.ethereum_bridge, abi.bridge, EthereumSDK.getSigner());
        if (!destination || destination.length < 32) {
            return setError(new Error('Invalid destination!'));
        }
        if (!amount || amount == '0') {
            return setError(new Error('Invalid amount!'));
        }

        try {
            const packed_destination = '0x' + IbcfSdk.Tezos.Utils.packAddress(destination);
            const result = await contract.wrap(packed_destination, amount);
            setConfirming(true);
            setOperationHash(result.hash);
            await result.wait(1);
        } catch (e: any) {
            Logger.error(e);
            return setError(e);
        } finally {
            setConfirming(false);
        }
    }, [destination, amount]);

    const handleDestination = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setDestination(e.target.value);
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
                                Ethereum
                            </Typography>
                        </Grid>
                        <Grid item>
                            <EthereumIcon />
                        </Grid>
                    </Grid>
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    {ethereum.clientStorage ? <AssetCard asset={ethereum.clientStorage?.asset} /> : null}
                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                    <Card variant="outlined">
                        <CardContent>
                            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                <Grid item>
                                    <Typography color="text.secondary">Bridge</Typography>
                                    <Typography variant="caption" fontSize={10}>
                                        <a
                                            target="_blank"
                                            style={{ color: 'white' }}
                                            href={`${Constants.etherscan}/address/${Constants.ethereum_bridge}`}
                                            rel="noreferrer"
                                        >
                                            {Constants.ethereum_bridge}
                                        </a>
                                    </Typography>
                                </Grid>
                                <Grid item>
                                    <Grid
                                        container
                                        direction="row"
                                        justifyContent="flex-end"
                                        alignItems="center"
                                        spacing={2}
                                    >
                                        <Grid item>
                                            <Button fullWidth size="small" onClick={() => setWrapModalOpen(true)}>
                                                Wrap
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                            <Card variant="outlined">
                                <CardContent>
                                    <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                        <Grid item>
                                            <Typography color="text.secondary" gutterBottom>
                                                Wraps
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <WrapsTable wraps={ethereum.clientStorage?.wraps || []} />
                                        </Grid>
                                    </Grid>
                                </CardContent>
                            </Card>
                        </CardContent>
                    </Card>
                </CardContent>
                <CardActions>
                    <Grid container direction="row" justifyContent="center" alignItems="center">
                        <Grid item>
                            <Typography color="text.secondary" gutterBottom>
                                {confirming ? 'Confirming...' : ''}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardActions>
            </Card>

            <Dialog
                title="Wrap token"
                open={wrapModalOpen}
                onClose={() => {
                    setWrapModalOpen(false);
                    setDestination(undefined);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={wrap}>
                            Wrap
                        </Button>
                    </DialogActions>
                }
            >
                <TextField
                    error={!destination}
                    placeholder="Destination (tz...)"
                    value={destination || ''}
                    onChange={handleDestination}
                    fullWidth
                    margin="dense"
                />
                <TextField value={amount || 0} placeholder="Amount" onChange={handleAmount} fullWidth margin="dense" />
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

export default Ethereum;
