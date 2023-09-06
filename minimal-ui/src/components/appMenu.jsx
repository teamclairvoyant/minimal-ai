import {useState} from 'react';
import {Button,Dialog,DialogContent,TextField,DialogActions} from '@mui/material';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import propTypes from "prop-types"
import Iconify from './Iconify';


AppMenu.propTypes = {
    menuName: propTypes.string,
    iconName: propTypes.string,
    buttonColor: propTypes.string,
    addNode: propTypes.func
}


function ShowTaskModal(openModal, setOpenModal,type,taskType, addNode,setAnchorEl){
    const[taskName, setTaskName] = useState('')

    
    return(
        <div>
            <Dialog open={openModal} onClose={() => setOpenModal(false)}>
                <DialogContent>
                    <TextField margin="dense" id="task-name" onChange={(e) => setTaskName(e.target.value)} label="Task Name" type="text" fullWidth variant="standard" />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenModal(false)}>Cancel</Button>
                    <Button onClick={() => {
                        addNode(type,taskName,taskType)
                        setOpenModal(false)
                        setAnchorEl(null)}}>
                    Create
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    )
}


function SourceMenu(menuName,addNode,setAnchorEl){
    const [open, setOpen] = useState(false)
    const [taskType, setTaskType] = useState('')

    function openTaskModal(sType){
        setOpen(true)
        setTaskType(sType)
    }

    if (menuName == "Source"){
        return (
            <div>
                <div>
                    <MenuItem onClick={() => openTaskModal("file")}>File</MenuItem>
                    <MenuItem onClick={() => openTaskModal("rdbms")}>Rdbms</MenuItem>
                </div>
                {ShowTaskModal(open, setOpen,'input',taskType,addNode,setAnchorEl)}
            </div>
        )
    }
    else if (menuName == "Transform") {
        return (
            <div>
                <div>
                    <MenuItem onClick={() => openTaskModal("join")}>Join</MenuItem>
                    <MenuItem onClick={() => openTaskModal("transform")}>Filter</MenuItem>
                    <MenuItem onClick={() => openTaskModal("transform")}>Group By</MenuItem>
                    <MenuItem onClick={() => openTaskModal("transform")}>Rename Column</MenuItem>
                </div>
                {ShowTaskModal(open, setOpen,'default',taskType,addNode,setAnchorEl)}
            </div>
        )
    }
    else {
        return (
            <div>
                <div>
                    <MenuItem onClick={() => openTaskModal("file")}>File</MenuItem>
                    <MenuItem onClick={() => openTaskModal("rdbms")}>Data Warehouse</MenuItem>
                </div>
                {ShowTaskModal(open, setOpen,'output',taskType,addNode,setAnchorEl)}
            </div>
        )
    }
}


export default function AppMenu({menuName, iconName, buttonColor, addNode}) {

    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    return (
        <div>
            <Button variant="outlined" onClick={(e) => setAnchorEl(e.currentTarget)} sx={{color:`${buttonColor}`,border:`1px solid ${buttonColor}`}} startIcon={<Iconify icon={iconName}/>}>
            {menuName}
                    </Button>
            
            <Menu
                id="basic-menu"
                anchorEl={anchorEl}
                open={open}
                onClose={() => setAnchorEl(null)}
                MenuListProps={{
                'aria-labelledby': 'basic-button',
                }}
            >
                {SourceMenu(menuName,addNode,setAnchorEl)}
            </Menu>
        </div>
    );
}
