import React from 'react';
import { Box, Container, Grid, Typography } from '@mui/material';
import AeternityIcon from 'src/components/base/icons/aeternity';
import EthereumIcon from 'src/components/base/icons/ethereum';

import TezosBridge from 'src/components/aeternity/bridge';
import EthereumBridge from 'src/components/ethereum/bridge';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';

const Bridge: React.FC = () => {
    return (
        <Container sx={{ paddingY: 8 }}>
            <Grid
                container
                direction="row"
                justifyContent="center"
                alignItems="flex-start"
                spacing={1}
                sx={{ marginBottom: 10 }}
            >
                <Card sx={{ minWidth: 400 }}>
                    <CardContent>
                        <Typography sx={{ fontSize: 18, marginBottom: 3 }} gutterBottom>
                            Bridge
                        </Typography>
                        <Typography sx={{ mb: 1.5 }} color="text.secondary">
                            From
                        </Typography>
                        <Grid container direction="row" spacing={1} sx={{ marginBottom: 2 }}>
                            <Grid item xs={7}>
                                <FormControl fullWidth>
                                    <InputLabel id="token-select-label">Token</InputLabel>
                                    <Select
                                        labelId="token-select-label"
                                        id="token-select"
                                        label="Token"
                                        defaultValue={10}
                                    >
                                        <MenuItem selected value={10}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>Æ</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>

                            <Grid item xs={5}>
                                <FormControl fullWidth>
                                    <InputLabel id="network-from-select-label">Network</InputLabel>
                                    <Select
                                        labelId="network-from-select-label"
                                        id="network-from-select"
                                        label="Network"
                                        defaultValue={10}
                                    >
                                        <MenuItem selected value={10}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon /> <Box sx={{ marginLeft: 1 }}>æternity</Box>
                                            </Box>
                                        </MenuItem>
                                        <MenuItem>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <EthereumIcon /> <Box sx={{ marginLeft: 1 }}>Ethereum</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>

                        <Typography sx={{ mb: 1.5 }} color="text.secondary">
                            To
                        </Typography>
                        <Grid container direction="row" spacing={1} sx={{ marginBottom: 3 }}>
                            <Grid item xs={7}>
                                <FormControl fullWidth>
                                    <InputLabel id="token-select-label">Token</InputLabel>
                                    <Select
                                        labelId="token-select-label"
                                        id="token-select"
                                        label="Token"
                                        defaultValue={10}
                                    >
                                        <MenuItem selected value={10}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon />
                                                <Box sx={{ marginLeft: 1 }}>wÆ</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={5}>
                                <FormControl fullWidth>
                                    <InputLabel id="network-to-select-label">Network</InputLabel>
                                    <Select
                                        labelId="network-to-select-label"
                                        id="network-to-select"
                                        label="Network"
                                        defaultValue={10}
                                    >
                                        <MenuItem selected value={10}>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <EthereumIcon /> <Box sx={{ marginLeft: 1 }}>Ethereum</Box>
                                            </Box>
                                        </MenuItem>
                                        <MenuItem>
                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                <AeternityIcon /> <Box sx={{ marginLeft: 1 }}>æternity</Box>
                                            </Box>
                                        </MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>

                        <TextField
                            fullWidth
                            id="outlined-basic"
                            label="Total Amount"
                            variant="outlined"
                            type="number"
                            sx={{ marginBottom: 2 }}
                        />

                        <TextField
                            fullWidth
                            id="outlined-basic"
                            label="Destination Address"
                            variant="outlined"
                            type="text"
                        />
                    </CardContent>
                    <CardActions sx={{ margin: 1, paddingTop: 6 }}>
                        <Button fullWidth variant="contained">
                            Connect Wallet
                        </Button>
                    </CardActions>
                </Card>
            </Grid>

            <Typography variant="overline">Bridging Steps</Typography>
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
