import React from 'react';
import { TextField as MuiTextField, TextFieldProps } from '@mui/material';

const TextField: React.FC<TextFieldProps> = (props) => {
    return <MuiTextField variant="outlined" {...props}></MuiTextField>;
};

export default TextField;
