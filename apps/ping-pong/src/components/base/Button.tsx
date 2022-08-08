import React from 'react';
import { Button as MuiButton, ButtonProps } from '@mui/material';

const Button: React.FC<ButtonProps & { component?: any }> = (props) => {
    return <MuiButton variant="outlined" {...props}></MuiButton>;
};

export default Button;
