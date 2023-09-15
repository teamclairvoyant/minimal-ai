/* eslint-disable no-unused-vars */
import { IconButton, ListItemIcon, ListItemText, Menu, MenuItem } from '@mui/material';
import PropTypes from "prop-types";
import { useRef, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { backendApi } from '../api/api';
import Iconify from '../components/Iconify';



TaskMoreMenu.propTypes = {
    pipeline_uuid: PropTypes.string
}

export default function TaskMoreMenu(props) {
    const ref = useRef(null);
    const [isOpen, setIsOpen] = useState(false);
    const [execDetails, setExecDetails]  = useState({})

    const execute = async (uuid) => {
        const response = await backendApi.get(`/pipeline/${uuid}/execute`);
        setExecDetails(await response.data());

    };

    return (
        <>
            <IconButton ref={ref} onClick={() => setIsOpen(true)}>
                <Iconify icon="eva:more-vertical-fill" width={20} height={20} />
            </IconButton>

            <Menu
                open={isOpen}
                anchorEl={ref.current}
                onClose={() => setIsOpen(false)}
                slotProps={{
                    sx: { width: 200, maxWidth: '100%' }
                }}
                anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            >
                <MenuItem sx={{ color: 'text.secondary' }}>
                    <ListItemIcon>
                        <Iconify icon="eva:trash-2-outline" width={24} height={24} />
                    </ListItemIcon>
                    <ListItemText primary="Delete" primaryTypographyProps={{ variant: 'body2' }} />
                </MenuItem>

                <MenuItem component={RouterLink} to="#" sx={{ color: 'text.secondary' }}>
                    <ListItemIcon>
                        <Iconify icon="eva:edit-fill" width={24} height={24} />
                    </ListItemIcon>
                    <ListItemText primary="Edit" primaryTypographyProps={{ variant: 'body2' }} />
                </MenuItem>
                <MenuItem onClick={() => execute(props.pipeline_uuid)} sx={{ color: 'text.secondary' }}>
                    <ListItemIcon>
                        <Iconify icon="eva:play-circle-outline" width={24} height={24} />
                    </ListItemIcon>
                    <ListItemText primary="Execute" primaryTypographyProps={{ variant: 'body2' }} />
                </MenuItem>
            </Menu>
        </>
    );
}
