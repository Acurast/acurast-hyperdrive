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
import Button from '../base/Button';

interface SubmissionRowProps {
    block_number: string;
    state_root: string;
    generateProof: (block_number: number) => void;
}

const SubmissionRow: React.FC<SubmissionRowProps> = ({ block_number, state_root, generateProof }) => {
    return (
        <TableRow>
            <TableCell component="th" scope="row" align="right">
                <Typography>{block_number}</Typography>
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
                <Typography variant="caption">{state_root}</Typography>
            </TableCell>
            <TableCell component="th" scope="row">
                <Button onClick={() => generateProof(Number(block_number))}>Get Proof</Button>
            </TableCell>
        </TableRow>
    );
};

interface OwnProps {
    submissions: [string, string][];
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
                            <TableCell>Block Number</TableCell>
                            <TableCell>State Root</TableCell>
                            <TableCell />
                        </MuiTableRow>
                    </MuiTableHead>
                }
                body={<MuiTableBody>{<Component {...props} />}</MuiTableBody>}
            />
        );

const ValidatedBlocksTable: React.FC<OwnProps> = ({ submissions, generateProof }) => {
    if (!submissions.length) {
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
            {submissions.map(([block_number, state_root], key) => (
                <SubmissionRow
                    key={key}
                    block_number={block_number}
                    state_root={state_root}
                    generateProof={generateProof}
                />
            ))}
        </>
    );
};

export default TableTemplate(ValidatedBlocksTable);
