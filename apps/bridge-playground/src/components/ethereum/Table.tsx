import React from 'react';
import {
    TableCell,
    TableHead as MuiTableHead,
    TableBody as MuiTableBody,
    TableRow as MuiTableRow,
    Box,
    Typography,
} from '@mui/material';
import { Ethereum } from '@ibcf/sdk';

import TableRow from 'src/components/base/TableRow';
import Table from '../base/Table';

const TRow: React.FC<Ethereum.Contracts.Bridge.Wrap> = ({ address, amount, nonce }) => {
    return (
        <TableRow>
            <TableCell component="th" scope="row">
                <Typography variant="caption">{address}</Typography>
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
    wraps: Ethereum.Contracts.Bridge.Wrap[];
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

const ValidatedBlocksTable: React.FC<OwnProps> = ({ wraps }) => {
    if (!wraps.length) {
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
            {wraps.map((wrap, key) => (
                <TRow key={key} {...wrap} />
            ))}
        </>
    );
};

export default TableTemplate(ValidatedBlocksTable);
