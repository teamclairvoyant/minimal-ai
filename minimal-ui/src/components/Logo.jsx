import PropTypes from 'prop-types';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Paper } from '@mui/material';
import {Typography} from '@mui/material';

Logo.propTypes = {
    disabledLink: PropTypes.bool,
    sx: PropTypes.object
};

export default function Logo({ disabledLink = false, sx }) {

    const logo = (
        <Paper sx={{ width: 65, ...sx }}>
            <img  src='../src/assets/images/EXL_Service_logo.png'/>
        </Paper>
    );

    if (disabledLink) {
        return <>{logo}</>;
    }

    return <RouterLink to="/">{logo}</RouterLink>;
}
