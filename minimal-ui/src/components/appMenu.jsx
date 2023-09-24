import { Button, Dialog, DialogActions, DialogContent, Stack, TextField } from '@mui/material';
import propTypes from "prop-types";
import { useState } from 'react';
import Iconify from './Iconify';


AppMenu.propTypes = {
    menuName: propTypes.string,
    type: propTypes.string,
    iconName: propTypes.string,
    buttonColor: propTypes.string,
    addNode: propTypes.func
}


function ShowTaskModal(openModal, setOpenModal, type, addNode) {
    const [taskName, setTaskName] = useState('')

    return (
        <div>
            <Dialog open={openModal} onClose={() => setOpenModal(false)}>
                <DialogContent>
                    <TextField margin="dense" id="task-name" onChange={(e) => setTaskName(e.target.value)} label="Task Name" type="text" fullWidth variant="standard" />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenModal(false)}>Cancel</Button>
                    <Button onClick={() => {
                        addNode(type, taskName)
                        setOpenModal(false)
                    }}
                    >
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    )
}


export default function AppMenu({ menuName, type, iconName, buttonColor, addNode }) {

    const [open, setOpen] = useState(false)

    return (
        <Stack>
            <Button variant="text" color='info' onClick={() => setOpen(true)}
                startIcon={<Iconify icon={iconName} />}
            >
                {menuName}
            </Button>
            {ShowTaskModal(open, setOpen, type, addNode)}
        </Stack>
    );
}
