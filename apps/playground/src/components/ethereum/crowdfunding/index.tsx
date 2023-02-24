import React from 'react';
import { Card, Grid, Typography, CardContent, CardActions, Divider, TextField, DialogActions } from '@mui/material';
import { ethers } from 'ethers';
import { Ethereum } from 'ibcf-sdk';

import EthereumSDK from 'src/services/ethereum';
import Button from 'src/components/base/Button';
import EthereumIcon from 'src/components/base/icons/ethereum';
import useAppContext from 'src/hooks/useAppContext';
import Table from './Table';
import Constants from 'src/constants';
import Dialog from '../../base/Dialog';
import Logger from 'src/services/logger';
import CodeBlock from 'src/components/base/CodeBlock';

const EthereumCrowdfunding = () => {
    const { ethereum, tezos, network } = useAppContext();
    const [operationHash, setOperationHash] = React.useState('');
    const [error, setError] = React.useState<Error>();
    const [modalOpen, setModalOpen] = React.useState(false);
    const [amount, setAmount] = React.useState<string>();
    const [confirming, setConfirming] = React.useState(false);
    const [proof, setProof] = React.useState<any>();

    const fund = React.useCallback(async () => {
        if (!amount || amount == '0') {
            return setError(new Error('Invalid amount!'));
        }

        try {
            const result = await EthereumSDK.getSigner().sendTransaction({
                to: Constants[network].evm_crowdfunding,
                value: amount,
            });
            setConfirming(true);
            setOperationHash(result.hash);
            await result.wait(1);
        } catch (e: any) {
            Logger.error(e);
            return setError(e);
        } finally {
            setConfirming(false);
        }
    }, [amount]);

    const handleAmount = React.useCallback((e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
        setAmount(e.target.value);
    }, []);

    const getProof = React.useCallback(
        async (nonce: number) => {
            const proofGenerator = new Ethereum.ProofGenerator(EthereumSDK);

            const hexNonce = nonce.toString(16).padStart(64, '0');
            const funderRegistryIndex = '2'.padStart(64, '0');
            const amountRegistryIndex = '3'.padStart(64, '0');
            const funderSlot = ethers.utils.keccak256('0x' + hexNonce + funderRegistryIndex);
            const amountSlot = ethers.utils.keccak256('0x' + hexNonce + amountRegistryIndex);

            const proof = await proofGenerator.generateStorageProof(
                Constants[network].evm_crowdfunding,
                [funderSlot, amountSlot],
                tezos.validatorInfo?.latestSnapshot.block_number,
            );

            setProof({
                block_number: tezos.validatorInfo?.latestSnapshot.block_number,
                nonce,
                account_proof_rlp: proof.account_proof_rlp,
                funder_proof_rlp: proof.storage_proofs_rlp[0],
                amount_proof_rlp: proof.storage_proofs_rlp[1],
            });
        },
        [tezos.validatorInfo?.latestSnapshot],
    );

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
                    <Card variant="outlined">
                        <CardContent>
                            <Grid container direction="row" justifyContent="space-between" alignItems="center">
                                <Grid item>
                                    <Typography color="text.secondary">Crowdfunding</Typography>
                                    <Typography variant="caption" fontSize={10}>
                                        <a
                                            target="_blank"
                                            style={{ color: 'white' }}
                                            href={`${Constants[network].etherscan}/address/${Constants[network].evm_crowdfunding}`}
                                            rel="noreferrer"
                                        >
                                            {Constants[network].evm_crowdfunding}
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
                                            <Button fullWidth size="small" onClick={() => setModalOpen(true)}>
                                                Fund
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
                                                Funding
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ marginTop: 2, marginBottom: 2 }} />
                                    <Grid container direction="row" justifyContent="center" alignItems="center">
                                        <Grid item>
                                            <Table
                                                funding={ethereum.crowdfundInfo?.funding || []}
                                                getProof={getProof}
                                            />
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
                title="Participate in crowdfund"
                open={modalOpen}
                onClose={() => {
                    setModalOpen(false);
                    setAmount(undefined);
                }}
                actions={
                    <DialogActions>
                        <Button fullWidth size="small" onClick={fund}>
                            Fund
                        </Button>
                    </DialogActions>
                }
            >
                <TextField value={amount || ''} placeholder="Amount" onChange={handleAmount} fullWidth margin="dense" />
            </Dialog>

            <Dialog title="Error" open={!!error} onClose={() => setError(undefined)}>
                {error?.message || ''}
            </Dialog>
            <Dialog title="Operation Hash" open={!!operationHash} onClose={() => setOperationHash('')}>
                <a
                    style={{ color: 'white' }}
                    target="_blank"
                    href={`${Constants[network].etherscan}/tx/${operationHash}`}
                    rel="noreferrer"
                >
                    Etherscan
                </a>
            </Dialog>

            <Dialog title="Proof" open={!!proof} onClose={() => setProof(undefined)}>
                {!!proof ? <CodeBlock language="json" code={JSON.stringify(proof, null, 2)} /> : ''}
            </Dialog>
        </>
    );
};

export default EthereumCrowdfunding;
