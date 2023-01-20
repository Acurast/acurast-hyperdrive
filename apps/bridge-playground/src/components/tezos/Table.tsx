import React from 'react';
import {
    TableCell,
    TableHead as MuiTableHead,
    TableBody as MuiTableBody,
    TableRow as MuiTableRow,
    Box,
    Typography,
} from '@mui/material';
import { Tezos } from '@ibcf/sdk';

import TableRow from 'src/components/base/TableRow';
import Table from '../base/Table';

const TRow: React.FC<Tezos.Contracts.Bridge.Unwrap> = ({ destination, amount, nonce }) => {
    return (
        <TableRow>
            <TableCell component="th" scope="row">
                <Typography variant="caption">{destination}</Typography>
            </TableCell>
            <TableCell
                component="th"
                scope="row"
                sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: 200,
                }}
            >
                <Typography variant="caption">{amount.toString()}</Typography>
            </TableCell>
            <TableCell component="th" scope="row">
                <Typography variant="caption">{nonce.toString()}</Typography>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    unwraps: Tezos.Contracts.Bridge.Unwrap[];
}

const TableTemplate =
    <T extends OwnProps>(Component: React.FC<T>): React.FC<T> =>
    (props) =>
        (
            <Table
                header={
                    <MuiTableHead>
                        <MuiTableRow>
                            <TableCell>Destination</TableCell>
                            <TableCell>Amount</TableCell>
                            <TableCell>Nonce</TableCell>
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const ValidatedBlocksTable: React.FC<OwnProps> = ({ unwraps }) => {
    if (!unwraps.length) {
        return (
            <MuiTableRow>
                <TableCell colSpan={6}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Typography variant="overline" textAlign="center">
                            No data
                        </Typography>
                    </Box>
                </TableCell>
            </MuiTableRow>
        );
    }

    return (
        <>
            {unwraps.map((unwrap, key) => (
                <TRow key={key} {...unwrap} />
            ))}
        </>
    );
};

export default TableTemplate(ValidatedBlocksTable);
