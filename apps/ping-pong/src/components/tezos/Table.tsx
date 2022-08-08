import React from 'react';
import {
    TableCell,
    TableHead as MuiTableHead,
    TableBody as MuiTableBody,
    TableRow as MuiTableRow,
    Box,
    Typography,
} from '@mui/material';

import TableRow from 'src/components/base/TableRow';
import Table from '../base/Table';
import BigNumber from 'bignumber.js';
import Button from '../base/Button';

interface MerkleRowProps {
    blockLevel: number;
    stateRoot: string;
    generateProof: (block_number: number) => void;
}

const MerkleRow: React.FC<MerkleRowProps> = ({ blockLevel, stateRoot, generateProof }) => {
    return (
        <TableRow>
            <TableCell component="th" scope="row" align="right">
                <Typography>{blockLevel}</Typography>
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
                <Typography variant="caption">{stateRoot}</Typography>
            </TableCell>
            <TableCell component="th" scope="row">
                <Button onClick={() => generateProof(blockLevel)}>Get Proof</Button>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    blocks: [BigNumber, string][];
    generateProof: (block_number: number) => void;
}

const TableTemplate =
    <T extends OwnProps>(Component: React.FC<T>): React.FC<T> =>
    // eslint-disable-next-line react/display-name
    (props) =>
        (
            <Table
                header={
                    <MuiTableHead>
                        <MuiTableRow>
                            <TableCell>Block Level</TableCell>
                            <TableCell>State Root</TableCell>
                            <TableCell />
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const MerkleTable: React.FC<OwnProps> = ({ blocks, generateProof }) => {
    if (!blocks.length) {
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
            {blocks.map(([blockLevel, stateRoot], key) => (
                <MerkleRow
                    key={key}
                    blockLevel={blockLevel.toNumber()}
                    stateRoot={stateRoot}
                    generateProof={generateProof}
                />
            ))}
        </>
    );
};

export default TableTemplate(MerkleTable);
